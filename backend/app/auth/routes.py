from flask import Blueprint, request, jsonify
from marshmallow import ValidationError

from app.auth.schema import RegisterSchema
from app.auth.service import AuthService

auth_bp = Blueprint("auth", __name__)

register_schema = RegisterSchema()


@auth_bp.route("/register", methods=["POST"])
def register():

    try:
        # Read JSON request
        data = request.get_json()

        # Validate request
        validated_data = register_schema.load(data)

        # Check password confirmation
        if validated_data["password"] != validated_data["confirm_password"]:
            return jsonify({
                "success": False,
                "message": "Passwords do not match."
            }), 400

        # Register user
        response, status_code = AuthService.register(validated_data)

        return jsonify(response), status_code

    except ValidationError as err:
        return jsonify({
            "success": False,
            "errors": err.messages
        }), 400

    except Exception as e:
        return jsonify({
            "success": False,
            "message": str(e)
        }), 500