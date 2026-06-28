from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.weather.service import WeatherService
from app.farm.service import FarmService

weather_bp = Blueprint("weather", __name__)


@weather_bp.route("/", methods=["GET"])
@jwt_required()
def get_weather():
    """
    Retrieve current weather and 7-day forecast for a farm using latitude and longitude.
    """
    try:
        farm_id = request.args.get("farm_id")
        if not farm_id:
            return jsonify({
                "success": False,
                "message": "farm_id query parameter is required."
            }), 400

        user_id = get_jwt_identity()

        # Check if farm exists and belongs to the user
        farm_res, status_code = FarmService.get_farm_by_id(farm_id, user_id)
        if status_code != 200:
            return jsonify(farm_res), status_code

        farm = farm_res["farm"]
        lat = farm.get("latitude")
        lon = farm.get("longitude")

        if lat is None or lon is None:
            return jsonify({
                "success": False,
                "message": "Selected farm has no latitude or longitude coordinates configured."
            }), 400

        response, status_code = WeatherService.get_weather_by_coords(lat, lon, farm_id)
        return jsonify(response), status_code

    except Exception as e:
        return jsonify({
            "success": False,
            "message": "An unexpected error occurred while fetching weather data.",
            "error": str(e)
        }), 500
