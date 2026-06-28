from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.dashboard.service import DashboardService

dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.route("/stats", methods=["GET"])
@jwt_required()
def get_dashboard_stats():
    """
    Fetch consolidated dashboard statistics for the authenticated user.
    """
    try:
        user_id = get_jwt_identity()
        response, status_code = DashboardService.get_dashboard_data(user_id)
        return jsonify(response), status_code

    except Exception as e:
        return jsonify({
            "success": False,
            "message": "An unexpected error occurred while fetching dashboard metrics.",
            "error": str(e)
        }), 500
