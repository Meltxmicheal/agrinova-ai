from app.models.prediction import Prediction
from app.ai.repository import AIRepository
from ml.predict import MLInferenceService
from app.farm.repository import FarmRepository
from app.services.soil_service import SoilService


class AIService:
    """
    AI Service
    Coordinates fertilizer recommendation logic.
    """

    @staticmethod
    def recommend_fertilizer(data: dict, user_id: str, soil_report_stream=None):
        try:
            # 1. Fetch Farm
            farm_id = data.get("farm_id")
            farm = FarmRepository.get_farm_by_id(farm_id)
            if not farm or farm.user_id != user_id:
                raise ValueError("Farm not found or unauthorized.")

            # 2. Get Soil Properties
            # Attempt OCR first if report is uploaded
            soil_props = None
            if soil_report_stream:
                try:
                    soil_props = SoilService.parse_soil_report(soil_report_stream)
                except Exception as e:
                    print(f"OCR Failed: {e}")
            
            # Fallback to coordinate-based soil data
            if not soil_props:
                soil_props = SoilService.get_soil_by_coords(farm.latitude or 20.0, farm.longitude or 77.0)

            # Predict best fertilizer
            recommended = MLInferenceService.recommend_fertilizer(
                soil_type=farm.soil_type,
                crop_type=data["crop_type"],
                nitrogen=soil_props["nitrogen"],
                phosphorus=soil_props["phosphorus"],
                potassium=soil_props["potassium"],
                moisture=soil_props.get("moisture", 45.0)
            )

            inputs = {
                "farm_name": farm.farm_name,
                "soil_type": farm.soil_type,
                "crop_type": data["crop_type"],
                "season": data.get("season", "Unknown"),
                "farming_goal": data.get("farming_goal", "Maximum Yield"),
                "estimated_nitrogen": soil_props["nitrogen"],
                "estimated_phosphorus": soil_props["phosphorus"],
                "estimated_potassium": soil_props["potassium"],
                "estimated_moisture": soil_props.get("moisture", 45.0),
                "source": "Soil Report (OCR)" if soil_report_stream else "Soil API Approximation"
            }

            outputs = {
                "recommended_fertilizer": recommended
            }

            # Create log entry
            prediction = Prediction(
                user_id=user_id,
                farm_id=farm_id,
                prediction_type="fertilizer_recommendation",
                inputs=inputs,
                outputs=outputs
            )

            AIRepository.save_prediction(prediction)

            return {
                "success": True,
                "prediction_id": str(prediction.id),
                "recommended_fertilizer": outputs["recommended_fertilizer"],
                "source": inputs["source"],
                "created_at": (
                    prediction.created_at.isoformat()
                    if prediction.created_at
                    else None
                )
            }, 200

        except Exception as e:
            AIRepository.rollback()
            return {
                "success": False,
                "message": "Failed to complete fertilizer recommendation.",
                "error": str(e)
            }, 500
