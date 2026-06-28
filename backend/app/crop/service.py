from app.models.prediction import Prediction
from app.crop.repository import CropRepository
from ml.predict import MLInferenceService
from app.farm.repository import FarmRepository
from app.services.soil_service import SoilService
from app.weather.service import WeatherService


class CropService:
    """
    Crop Service
    Orchestrates inputs for the ML engine and records recommendations in history.
    """

    @staticmethod
    def recommend_crop(data: dict, user_id: str, soil_report_stream=None):
        try:
            # 1. Fetch Farm
            farm_id = data.get("farm_id")
            farm = FarmRepository.get_farm_by_id(farm_id)
            if not farm or farm.user_id != user_id:
                raise ValueError("Farm not found or unauthorized.")

            # 2. Get Soil Properties
            soil_props = None
            if soil_report_stream:
                try:
                    soil_props = SoilService.parse_soil_report(soil_report_stream)
                except Exception as e:
                    print(f"OCR Failed: {e}")
            
            if not soil_props:
                soil_props = SoilService.get_soil_by_coords(farm.latitude or 20.0, farm.longitude or 77.0)

            # 3. Get Weather — summary dict is populated even on partial data
            weather_resp, _status = WeatherService.get_weather_by_coords(
                lat=farm.latitude or 20.0,
                lon=farm.longitude or 77.0,
                farm_id=farm_id
            )
            current_weather = weather_resp.get("weather", {}).get("current", {})
            weather_summary  = weather_resp.get("weather", {}).get("summary", {})

            temperature = weather_summary.get("temperature") or current_weather.get("temp", 25.0)
            humidity    = weather_summary.get("humidity")    or current_weather.get("humidity", 60.0)
            # Estimate rainfall: rain_probability (0-100 %) → approximate mm
            rain_prob = weather_summary.get("rain_probability") or current_weather.get("rain_probability", 20.0)
            rainfall  = round(rain_prob * 0.3, 2)  # rough mm estimate

            # Execute model prediction
            recommended = MLInferenceService.recommend_crop(
                N=soil_props["nitrogen"],
                P=soil_props["phosphorus"],
                K=soil_props["potassium"],
                temperature=temperature,
                humidity=humidity,
                ph=soil_props["ph"],
                rainfall=rainfall
            )

            inputs = {
                "farm_name": farm.farm_name,
                "season": data.get("season", "Unknown"),
                "farming_goal": data.get("farming_goal", "Maximum Yield"),
                "estimated_nitrogen": soil_props["nitrogen"],
                "estimated_phosphorus": soil_props["phosphorus"],
                "estimated_potassium": soil_props["potassium"],
                "estimated_ph": soil_props["ph"],
                "estimated_temperature": temperature,
                "estimated_humidity": humidity,
                "estimated_rainfall": rainfall,
                "source": "Soil Report (OCR)" if soil_report_stream else "Soil API Approximation"
            }
            
            outputs = {
                "recommended_crop": recommended.capitalize()
            }

            # Create DB Log entry
            prediction = Prediction(
                user_id=user_id,
                farm_id=farm_id,
                prediction_type="crop_recommendation",
                inputs=inputs,
                outputs=outputs
            )

            # Persist prediction in DB
            CropRepository.save_prediction(prediction)

            return {
                "success": True,
                "prediction_id": str(prediction.id),
                "recommended_crop": outputs["recommended_crop"],
                "source": inputs["source"],
                "created_at": (
                    prediction.created_at.isoformat()
                    if prediction.created_at
                    else None
                )
            }, 200

        except Exception as e:
            CropRepository.rollback()
            return {
                "success": False,
                "message": "Failed to complete crop recommendation prediction.",
                "error": str(e)
            }, 500
