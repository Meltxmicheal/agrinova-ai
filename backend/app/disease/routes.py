from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.disease.service import DiseaseService

disease_bp = Blueprint("disease", __name__)


@disease_bp.route("/detect", methods=["POST"])
@jwt_required()
def detect_disease():
    """
    Upload a leaf image and return classified plant disease status.
    """
    try:
        # Check if file exists in request
        if "file" not in request.files:
            return jsonify({
                "success": False,
                "message": "No file uploaded. Please include 'file' key in multi-part form."
            }), 400

        file = request.files["file"]

        if file.filename == "":
            return jsonify({
                "success": False,
                "message": "Empty file name."
            }), 400

        # Optional farm_id link
        farm_id = request.form.get("farm_id")
        if farm_id == "null" or farm_id == "":
            farm_id = None

        user_id = get_jwt_identity()

        response, status_code = DiseaseService.detect_disease(file, farm_id, user_id)
        return jsonify(response), status_code

    except Exception as e:
        return jsonify({
            "success": False,
            "message": "An unexpected error occurred during disease detection.",
            "error": str(e)
        }), 500
