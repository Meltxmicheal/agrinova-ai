from flask import Blueprint, request, jsonify
from marshmallow import ValidationError
from flask_jwt_extended import jwt_required, get_jwt_identity

from app.farm.schema import FarmSchema
from app.farm.service import FarmService

farm_bp = Blueprint("farm", __name__)

farm_schema = FarmSchema()


# =====================================================
# Create Farm
# =====================================================
@farm_bp.route("/", methods=["POST"])
@jwt_required()
def create_farm():
    """
    Create a new farm.
    """

    try:
        data = request.get_json()

        if not data:
            return jsonify({
                "success": False,
                "message": "Request body cannot be empty."
            }), 400

        validated_data = farm_schema.load(data)

        user_id = get_jwt_identity()

        response, status_code = FarmService.create_farm(
            validated_data,
            user_id
        )

        return jsonify(response), status_code

    except ValidationError as err:
        return jsonify({
            "success": False,
            "errors": err.messages
        }), 400

    except Exception as e:
        return jsonify({
            "success": False,
            "message": "Internal Server Error",
            "error": str(e)
        }), 500


# =====================================================
# Get All Farms
# =====================================================
@farm_bp.route("/", methods=["GET"])
@jwt_required()
def get_farms():
    """
    Get all farms of the logged-in user.
    """

    try:

        user_id = get_jwt_identity()

        response, status_code = FarmService.get_all_farms(user_id)

        return jsonify(response), status_code

    except Exception as e:

        return jsonify({
            "success": False,
            "message": "Internal Server Error",
            "error": str(e)
        }), 500


# =====================================================
# Get Single Farm
# =====================================================
@farm_bp.route("/<string:id>", methods=["GET"])
@jwt_required()
def get_farm(id):
    """
    Get farm by ID.
    """
    try:
        user_id = get_jwt_identity()
        response, status_code = FarmService.get_farm_by_id(id, user_id)
        return jsonify(response), status_code
    except Exception as e:
        return jsonify({
            "success": False,
            "message": "Internal Server Error",
            "error": str(e)
        }), 500


# =====================================================
# Update Farm
# =====================================================
@farm_bp.route("/<string:id>", methods=["PUT"])
@jwt_required()
def update_farm(id):
    """
    Update farm by ID.
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                "success": False,
                "message": "Request body cannot be empty."
            }), 400

        # Allow partial updates
        validated_data = farm_schema.load(data, partial=True)

        user_id = get_jwt_identity()
        response, status_code = FarmService.update_farm(id, validated_data, user_id)
        return jsonify(response), status_code

    except ValidationError as err:
        return jsonify({
            "success": False,
            "errors": err.messages
        }), 400

    except Exception as e:
        return jsonify({
            "success": False,
            "message": "Internal Server Error",
            "error": str(e)
        }), 500


# =====================================================
# Delete Farm
# =====================================================
@farm_bp.route("/<string:id>", methods=["DELETE"])
@jwt_required()
def delete_farm(id):
    """
    Delete farm by ID.
    """
    try:
        user_id = get_jwt_identity()
        response, status_code = FarmService.delete_farm(id, user_id)
        return jsonify(response), status_code
    except Exception as e:
        return jsonify({
            "success": False,
            "message": "Internal Server Error",
            "error": str(e)
        }), 500