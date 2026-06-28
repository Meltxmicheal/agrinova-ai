from flask import Blueprint, request, jsonify
from marshmallow import ValidationError
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.prediction.schema import YieldPredictionSchema, PricePredictionSchema
from app.prediction.service import PredictionService

prediction_bp = Blueprint("prediction", __name__)
yield_schema = YieldPredictionSchema()
price_schema = PricePredictionSchema()


@prediction_bp.route("/yield", methods=["POST"])
@jwt_required()
def predict_yield():
    """
    Perform yield prediction based on area, weather, and crop factors.
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                "success": False,
                "message": "Request body cannot be empty."
            }), 400

        validated_data = yield_schema.load(data)
        user_id = get_jwt_identity()

        response, status_code = PredictionService.predict_yield(validated_data, user_id)
        return jsonify(response), status_code

    except ValidationError as err:
        return jsonify({
            "success": False,
            "errors": err.messages
        }), 400

    except Exception as e:
        return jsonify({
            "success": False,
            "message": "An unexpected error occurred during yield prediction.",
            "error": str(e)
        }), 500


@prediction_bp.route("/price", methods=["POST"])
@jwt_required()
def predict_price():
    """
    Perform market price prediction based on commodity and seasonal parameters.
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                "success": False,
                "message": "Request body cannot be empty."
            }), 400

        validated_data = price_schema.load(data)
        user_id = get_jwt_identity()

        response, status_code = PredictionService.predict_market_price(validated_data, user_id)
        return jsonify(response), status_code

    except ValidationError as err:
        return jsonify({
            "success": False,
            "errors": err.messages
        }), 400

    except Exception as e:
        return jsonify({
            "success": False,
            "message": "An unexpected error occurred during market price prediction.",
            "error": str(e)
        }), 500
