import os
from werkzeug.utils import secure_filename
from app.models.prediction import Prediction
from app.disease.repository import DiseaseRepository
from ml.predict import MLInferenceService

# Configure upload path within the workspace
UPLOAD_FOLDER = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../uploads"))
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


class DiseaseService:
    """
    Disease Service
    Saves leaf image files and runs analysis on them.
    """

    @staticmethod
    def detect_disease(file, farm_id: str, user_id: str):
        try:
            # 1. Secure filename and save to local disk
            filename = secure_filename(file.filename)
            file_path = os.path.join(UPLOAD_FOLDER, filename)
            file.save(file_path)

            # 2. Perform ML Inference
            result = MLInferenceService.detect_disease(file_path)

            # 3. Save logs
            inputs = {
                "image_filename": filename
            }
            outputs = {
                "disease_name": result["disease_name"],
                "confidence": result["confidence"],
                "treatment": result["treatment"],
                "pesticide_recommendation": result["pesticide_recommendation"],
                "organic_alternative": result["organic_alternative"]
            }

            prediction = Prediction(
                user_id=user_id,
                farm_id=farm_id,
                prediction_type="disease_detection",
                inputs=inputs,
                outputs=outputs,
                confidence=result["confidence"]
            )

            # Save in database
            DiseaseRepository.save_prediction(prediction)

            return {
                "success": True,
                "prediction_id": str(prediction.id),
                "disease_name": result["disease_name"],
                "confidence": result["confidence"],
                "treatment": result["treatment"],
                "pesticide_recommendation": result["pesticide_recommendation"],
                "organic_alternative": result["organic_alternative"],
                "created_at": (
                    prediction.created_at.isoformat()
                    if prediction.created_at
                    else None
                )
            }, 200

        except Exception as e:
            DiseaseRepository.rollback()
            return {
                "success": False,
                "message": "Failed to analyze leaf image.",
                "error": str(e)
            }, 500
