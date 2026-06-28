from flask import Blueprint, request, jsonify

from app.auth.service import register_user

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/register", methods=["POST"])
def register():

    data = request.get_json()

    user = register_user(data)

    return jsonify({
        "success": True,
        "message": "User Registered Successfully",
        "user": {
            "id": user.id,
            "name": user.full_name,
            "email": user.email
        }
    }), 201