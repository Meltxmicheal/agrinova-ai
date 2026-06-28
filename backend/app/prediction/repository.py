from app.models.prediction import Prediction
from app.extensions import db


class PredictionRepository:
    """
    Prediction Repository
    Handles database operations for yield and market price predictions.
    """

    @staticmethod
    def save_prediction(prediction: Prediction) -> Prediction:
        db.session.add(prediction)
        db.session.commit()
        return prediction

    @staticmethod
    def rollback():
        db.session.rollback()
