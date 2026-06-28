from app.models.user import User
from app.extensions import db


class AuthRepository:
    """
    Repository Layer
    Handles all database operations related to authentication.
    """

    @staticmethod
    def get_user_by_email(email):
        """
        Get user by email.
        """
        return User.query.filter_by(email=email).first()

    @staticmethod
    def get_user_by_phone(phone):
        """
        Get user by phone number.
        """
        return User.query.filter_by(phone=phone).first()

    @staticmethod
    def get_user_by_id(user_id):
        """
        Get user by ID.
        """
        return User.query.filter_by(id=user_id).first()

    @staticmethod
    def create_user(user):
        """
        Save a new user.
        """
        db.session.add(user)
        db.session.commit()
        return user

    @staticmethod
    def update_user():
        """
        Commit pending changes.
        """
        db.session.commit()

    @staticmethod
    def delete_user(user):
        """
        Delete a user.
        """
        db.session.delete(user)
        db.session.commit()

    @staticmethod
    def rollback():
        """
        Rollback current transaction.
        """
        db.session.rollback()