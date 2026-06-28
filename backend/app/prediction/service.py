from app.models.prediction import Prediction
from app.prediction.repository import PredictionRepository
from ml.predict import MLInferenceService
from app.farm.repository import FarmRepository
from app.weather.service import WeatherService
from app.services.soil_service import SoilService


class PredictionService:
    """
    Prediction Service
    Executes yield and market price predictions and logs them in history.
    """

    @staticmethod
    def predict_yield(data: dict, user_id: str):
        try:
            # 1. Fetch Farm
            farm_id = data.get("farm_id")
            farm = FarmRepository.get_farm_by_id(farm_id)
            if not farm or farm.user_id != user_id:
                raise ValueError("Farm not found or unauthorized.")

            # 2. Fetch Weather via Open-Meteo
            weather_resp, _status = WeatherService.get_weather_by_coords(
                lat=farm.latitude or 20.0,
                lon=farm.longitude or 77.0,
                farm_id=farm_id
            )
            current_weather = weather_resp.get("weather", {}).get("current", {})
            weather_summary  = weather_resp.get("weather", {}).get("summary", {})

            temperature = weather_summary.get("temperature") or current_weather.get("temp", 25.0)
            rain_prob   = weather_summary.get("rain_probability") or current_weather.get("rain_probability", 20.0)
            rainfall    = round(rain_prob * 0.3, 2)  # rough mm estimate

            # Predict yield in tonnes
            predicted_yield = MLInferenceService.predict_yield(
                state=farm.state,
                crop=data["crop"],
                season=data["season"],
                area=farm.farm_size,
                rainfall=rainfall,
                temperature=temperature
            )

            inputs = {
                "farm_name": farm.farm_name,
                "state": farm.state,
                "crop": data["crop"],
                "season": data["season"],
                "area": farm.farm_size,
                "rainfall_estimated": round(rainfall, 2),
                "temperature_estimated": round(temperature, 2)
            }

            outputs = {
                "predicted_yield_tonnes": predicted_yield,
                "yield_per_hectare": round(predicted_yield / farm.farm_size, 2) if farm.farm_size > 0 else 0
            }

            # Create log entry
            prediction = Prediction(
                user_id=user_id,
                farm_id=farm_id,
                prediction_type="yield_prediction",
                inputs=inputs,
                outputs=outputs
            )

            PredictionRepository.save_prediction(prediction)

            return {
                "success": True,
                "prediction_id": str(prediction.id),
                "predicted_yield": outputs["predicted_yield_tonnes"],
                "yield_per_hectare": outputs["yield_per_hectare"],
                "created_at": (
                    prediction.created_at.isoformat()
                    if prediction.created_at
                    else None
                )
            }, 200

        except Exception as e:
            PredictionRepository.rollback()
            return {
                "success": False,
                "message": "Failed to complete yield prediction.",
                "error": str(e)
            }, 500

    @staticmethod
    def predict_market_price(data: dict, user_id: str):
        try:
            # Fetch Farm
            farm_id = data.get("farm_id")
            farm = FarmRepository.get_farm_by_id(farm_id)
            if not farm or farm.user_id != user_id:
                raise ValueError("Farm not found or unauthorized.")

            # Predict market price
            predicted_price = MLInferenceService.predict_market_price(
                state=farm.state,
                district=farm.district,
                commodity=data["commodity"],
                month=data["month"]
            )

            inputs = {
                "farm_name": farm.farm_name,
                "state": farm.state,
                "district": farm.district,
                "commodity": data["commodity"],
                "month": data["month"]
            }

            outputs = {
                "predicted_price_inr_quintal": predicted_price
            }

            # Create log entry
            prediction = Prediction(
                user_id=user_id,
                farm_id=farm_id,
                prediction_type="market_price_prediction",
                inputs=inputs,
                outputs=outputs
            )

            PredictionRepository.save_prediction(prediction)

            return {
                "success": True,
                "prediction_id": str(prediction.id),
                "predicted_price": outputs["predicted_price_inr_quintal"],
                "created_at": (
                    prediction.created_at.isoformat()
                    if prediction.created_at
                    else None
                )
            }, 200

        except Exception as e:
            PredictionRepository.rollback()
            return {
                "success": False,
                "message": "Failed to complete market price prediction.",
                "error": str(e)
            }, 500
