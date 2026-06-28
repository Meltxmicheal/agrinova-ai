from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.assistant.service import AssistantService

assistant_bp = Blueprint("assistant", __name__)

@assistant_bp.route("/chat", methods=["POST"])
@jwt_required()
def chat():
    """
    Handle chat messages for the AI Farm Assistant.
    """
    try:
        data = request.get_json()
        message = data.get("message")
        history = data.get("history", [])

        if not message:
            return jsonify({
                "success": False,
                "message": "Message is required."
            }), 400

        user_id = get_jwt_identity()
        response, status = AssistantService.handle_chat(user_id, message, history)
        
        return jsonify(response), status

    except Exception as e:
        return jsonify({
            "success": False,
            "message": "An unexpected error occurred during chat.",
            "error": str(e)
        }), 500
