import uuid
from datetime import datetime
from app.extensions import db


class WeatherHistory(db.Model):
    """
    Weather History Model
    Stores historical weather polling data for farms.
    """

    __tablename__ = "weather_history"

    id = db.Column(
        db.String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4())
    )

    farm_id = db.Column(
        db.String(36),
        db.ForeignKey("farms.id"),
        nullable=False
    )

    temperature = db.Column(db.Float, nullable=False)
    humidity = db.Column(db.Float, nullable=False)
    wind_speed = db.Column(db.Float, nullable=False)
    rain_probability = db.Column(db.Float, nullable=True, default=0.0)
    weather_description = db.Column(db.String(100), nullable=False)
    polled_at = db.Column(db.DateTime, default=datetime.utcnow)

    farm = db.relationship("Farm", backref=db.backref("weather_logs", cascade="all, delete-orphan"), lazy=True)

    def __repr__(self):
        return f"<WeatherHistory {self.weather_description} temp={self.temperature} farm={self.farm_id}>"
