from app.models.farm import Farm
from app.models.prediction import Prediction
from app.models.weather import WeatherHistory
from app.extensions import db


class DashboardRepository:
    """
    Dashboard Repository
    Queries database metrics and logs for farm, weather, and prediction counts.
    """

    @staticmethod
    def get_stats_by_user(user_id: str) -> dict:
        farms_count = Farm.query.filter_by(user_id=user_id).count()
        total_size = (
            db.session.query(db.func.sum(Farm.farm_size))
            .filter(Farm.user_id == user_id)
            .scalar()
            or 0.0
        )

        predictions_count = Prediction.query.filter_by(user_id=user_id).count()

        # Breakdown of predictions
        crop_count = Prediction.query.filter_by(
            user_id=user_id, prediction_type="crop_recommendation"
        ).count()
        yield_count = Prediction.query.filter_by(
            user_id=user_id, prediction_type="yield_prediction"
        ).count()
        fert_count = Prediction.query.filter_by(
            user_id=user_id, prediction_type="fertilizer_recommendation"
        ).count()
        disease_count = Prediction.query.filter_by(
            user_id=user_id, prediction_type="disease_detection"
        ).count()
        price_count = Prediction.query.filter_by(
            user_id=user_id, prediction_type="market_price_prediction"
        ).count()

        # Recent activities
        recent_predictions = (
            Prediction.query.filter_by(user_id=user_id)
            .order_by(Prediction.created_at.desc())
            .limit(5)
            .all()
        )

        # Get weather history for all user's farms
        user_farms = Farm.query.filter_by(user_id=user_id).all()
        user_farm_ids = [str(f.id) for f in user_farms]
        recent_weather = []

        if user_farm_ids:
            recent_weather = (
                WeatherHistory.query.filter(WeatherHistory.farm_id.in_(user_farm_ids))
                .order_by(WeatherHistory.polled_at.desc())
                .limit(5)
                .all()
            )

        return {
            "farms_count": farms_count,
            "total_size": float(total_size),
            "predictions_count": predictions_count,
            "breakdown": {
                "crop": crop_count,
                "yield": yield_count,
                "fertilizer": fert_count,
                "disease": disease_count,
                "price": price_count
            },
            "recent_predictions": recent_predictions,
            "recent_weather": recent_weather
        }
