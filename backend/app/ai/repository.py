from app.models.prediction import Prediction
from app.extensions import db


class AIRepository:
    """
    AI Repository
    Persists AI predictions like fertilizer recommendation to the database.
    """

    @staticmethod
    def save_prediction(prediction: Prediction) -> Prediction:
        db.session.add(prediction)
        db.session.commit()
        return prediction

    @staticmethod
    def rollback():
        db.session.rollback()
