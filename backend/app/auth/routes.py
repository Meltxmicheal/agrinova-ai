from flask import Blueprint, request, jsonify
from marshmallow import ValidationError
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.auth.repository import AuthRepository
from app.auth.schema import RegisterSchema
from app.auth.login_schema import LoginSchema
from app.auth.service import AuthService

auth_bp = Blueprint("auth", __name__)

register_schema = RegisterSchema()
login_schema = LoginSchema()


# =====================================================
# Register API
# =====================================================
@auth_bp.route("/register", methods=["POST"])
def register():
    """
    Register a new user.
    """

    try:
        data = request.get_json()

        if not data:
            return jsonify({
                "success": False,
                "message": "Request body cannot be empty."
            }), 400

        validated_data = register_schema.load(data)

        if validated_data["password"] != validated_data["confirm_password"]:
            return jsonify({
                "success": False,
                "message": "Passwords do not match."
            }), 400

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
            "message": "Internal Server Error",
            "error": str(e)
        }), 500


# =====================================================
# Login API
# =====================================================
@auth_bp.route("/login", methods=["POST"])
def login():
    """
    Authenticate user.
    """

    try:
        data = request.get_json()

        if not data:
            return jsonify({
                "success": False,
                "message": "Request body cannot be empty."
            }), 400

        validated_data = login_schema.load(data)

        response, status_code = AuthService.login(validated_data)

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
# Profile API
# =====================================================
@auth_bp.route("/profile", methods=["GET"])
@jwt_required()
def profile():
    """
    Get logged in user profile.
    """

    try:

        user_id = get_jwt_identity()

        user = AuthRepository.get_user_by_id(user_id)

        if not user:
            return jsonify({
                "success": False,
                "message": "User not found."
            }), 404

        return jsonify({

            "success": True,

            "user": {

                "id": str(user.id),
                "full_name": user.full_name,
                "email": user.email,
                "phone": user.phone,
                "is_verified": user.is_verified,
                "created_at": (
                    user.created_at.isoformat()
                    if user.created_at
                    else None
                )

            }

        }), 200

    except Exception as e:

        return jsonify({
            "success": False,
            "message": "Failed to fetch profile.",
            "error": str(e)
        }), 500


# =====================================================
# Logout API
# =====================================================
@auth_bp.route("/logout", methods=["POST"])
@jwt_required()
def logout():
    """
    Log out the current user (token revocation).
    """
    try:
        # In this stateless setup, client will discard tokens.
        # Can be integrated with blocklist in database if needed.
        return jsonify({
            "success": True,
            "message": "Logged out successfully."
        }), 200
    except Exception as e:
        return jsonify({
            "success": False,
            "message": "Logout failed.",
            "error": str(e)
        }), 500


# =====================================================
# Refresh Token API
# =====================================================
@auth_bp.route("/refresh", methods=["POST"])
@jwt_required(refresh=True)
def refresh():
    """
    Generates a new access token using a refresh token.
    """
    try:
        user_id = get_jwt_identity()
        response, status_code = AuthService.refresh_token(user_id)
        return jsonify(response), status_code
    except Exception as e:
        return jsonify({
            "success": False,
            "message": "Token refresh failed.",
            "error": str(e)
        }), 500


# =====================================================
# Forgot Password API
# =====================================================
@auth_bp.route("/forgot-password", methods=["POST"])
def forgot_password():
    """
    Request a password reset link.
    """
    try:
        data = request.get_json()
        if not data or "email" not in data:
            return jsonify({
                "success": False,
                "message": "Email is required."
            }), 400

        response, status_code = AuthService.forgot_password(data["email"])
        return jsonify(response), status_code
    except Exception as e:
        return jsonify({
            "success": False,
            "message": "Password reset request failed.",
            "error": str(e)
        }), 500


# =====================================================
# Reset Password API
# =====================================================
@auth_bp.route("/reset-password", methods=["POST"])
def reset_password():
    """
    Reset user password using a token.
    """
    try:
        data = request.get_json()
        if not data or "token" not in data or "new_password" not in data:
            return jsonify({
                "success": False,
                "message": "Token and new_password are required."
            }), 400

        response, status_code = AuthService.reset_password(data["token"], data["new_password"])
        return jsonify(response), status_code
    except Exception as e:
        return jsonify({
            "success": False,
            "message": "Password reset failed.",
            "error": str(e)
        }), 500