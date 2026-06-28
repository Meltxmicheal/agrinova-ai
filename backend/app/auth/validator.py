from app.models.user import User
from app.extensions import db


class AuthRepository:

    @staticmethod
    def get_user_by_email(email):
        return User.query.filter_by(email=email).first()

    @staticmethod
    def get_user_by_phone(phone):
        return User.query.filter_by(phone=phone).first()

    @staticmethod
    def create_user(user):
        db.session.add(user)
        db.session.commit()
        return user

    @staticmethod
    def rollback():
        db.session.rollback()