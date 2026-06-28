from app.models.prediction import Prediction
from app.extensions import db


class DiseaseRepository:
    """
    Disease Repository
    Logs plant disease detection predictions to the database.
    """

    @staticmethod
    def save_prediction(prediction: Prediction) -> Prediction:
        db.session.add(prediction)
        db.session.commit()
        return prediction

    @staticmethod
    def rollback():
        db.session.rollback()
