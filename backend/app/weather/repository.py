from app.models.weather import WeatherHistory
from app.extensions import db


class WeatherRepository:
    """
    Weather Repository
    Handles database operations for WeatherHistory.
    """

    @staticmethod
    def save_weather_history(weather_log: WeatherHistory) -> WeatherHistory:
        db.session.add(weather_log)
        db.session.commit()
        return weather_log

    @staticmethod
    def get_history_by_farm(farm_id: str, limit: int = 10) -> list:
        return (
            WeatherHistory.query.filter_by(farm_id=farm_id)
            .order_by(WeatherHistory.polled_at.desc())
            .limit(limit)
            .all()
        )

    @staticmethod
    def rollback():
        db.session.rollback()
