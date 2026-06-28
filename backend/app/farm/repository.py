from app.models.farm import Farm
from app.extensions import db


class FarmRepository:
    """
    Repository Layer
    Handles all database operations related to farms.
    """

    @staticmethod
    def create_farm(farm):
        db.session.add(farm)
        db.session.commit()
        return farm

    @staticmethod
    def get_farms_by_user(user_id):
        return Farm.query.filter_by(user_id=user_id).all()

    @staticmethod
    def get_farm_by_id(farm_id):
        return Farm.query.filter_by(id=farm_id).first()

    @staticmethod
    def update():
        db.session.commit()

    @staticmethod
    def delete(farm):
        db.session.delete(farm)
        db.session.commit()

    @staticmethod
    def rollback():
        db.session.rollback()

    @staticmethod
    def update_farm():
        db.session.commit()


    @staticmethod
    def delete_farm(farm):
        db.session.delete(farm)
        db.session.commit()