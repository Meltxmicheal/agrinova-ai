from flask import Blueprint, request, jsonify
from marshmallow import ValidationError
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.ai.schema import FertilizerRecommendationSchema
from app.ai.service import AIService

ai_bp = Blueprint("ai", __name__)
fertilizer_schema = FertilizerRecommendationSchema()


@ai_bp.route("/fertilizer", methods=["POST"])
@jwt_required()
def recommend_fertilizer():
    """
    Generate fertilizer recommendation based on soil and crop properties.
    Supports JSON or multipart/form-data (for soil test upload).
    """
    try:
        # Check if form-data or json
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

        validated_data = fertilizer_schema.load(data)
        user_id = get_jwt_identity()

        response, status_code = AIService.recommend_fertilizer(validated_data, user_id, soil_report_stream=file_stream)
        return jsonify(response), status_code

    except ValidationError as err:
        return jsonify({
            "success": False,
            "errors": err.messages
        }), 400

    except Exception as e:
        return jsonify({
            "success": False,
            "message": "An unexpected error occurred during fertilizer recommendation.",
            "error": str(e)
        }), 500
