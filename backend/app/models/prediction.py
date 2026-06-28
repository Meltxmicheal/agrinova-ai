import uuid
from datetime import datetime
from app.extensions import db


class Prediction(db.Model):
    """
    Prediction Model
    Stores input parameters and prediction results for all AI modules.
    """

    __tablename__ = "predictions"

    id = db.Column(
        db.String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4())
    )

    user_id = db.Column(
        db.String(36),
        db.ForeignKey("users.id"),
        nullable=False
    )

    farm_id = db.Column(
        db.String(36),
        db.ForeignKey("farms.id"),
        nullable=True
    )

    prediction_type = db.Column(
        db.String(50),
        nullable=False
    )  # crop_recommendation, yield_prediction, disease_detection, fertilizer_recommendation, market_price_prediction

    inputs = db.Column(
        db.JSON,
        nullable=False
    )

    outputs = db.Column(
        db.JSON,
        nullable=False
    )

    confidence = db.Column(
        db.Float,
        nullable=True
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    user = db.relationship("User", backref="predictions", lazy=True)
    farm = db.relationship("Farm", backref="predictions", lazy=True)

    def __repr__(self):
        return f"<Prediction type={self.prediction_type} user={self.user_id} date={self.created_at}>"
