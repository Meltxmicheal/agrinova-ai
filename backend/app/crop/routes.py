from flask import Blueprint, request, jsonify
from marshmallow import ValidationError
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.crop.schema import CropRecommendationSchema
from app.crop.service import CropService

crop_bp = Blueprint("crop", __name__)
crop_schema = CropRecommendationSchema()

@crop_bp.route("/recommend", methods=["POST"])
@jwt_required()
def recommend_crop():
    """
    Recommend the best crop. Supports multipart/form-data for OCR or JSON.
    """
    try:
        if request.content_type and "multipart/form-data" in request.content_type:
            data = request.form.to_dict()
            file_stream = request.files.get("soil_report")
        else:
            data = request.get_json()
            file_stream = None

        if not data:
            return jsonify({
                "success": False,
                "message": "Request body cannot be empty."
            }), 400

        validated_data = crop_schema.load(data)
        user_id = get_jwt_identity()

        response, status_code = CropService.recommend_crop(validated_data, user_id, soil_report_stream=file_stream)
        return jsonify(response), status_code

    except ValidationError as err:
        return jsonify({
            "success": False,
            "errors": err.messages
        }), 400

    except Exception as e:
        return jsonify({
            "success": False,
            "message": "An unexpected error occurred during crop recommendation.",
            "error": str(e)
        }), 500
