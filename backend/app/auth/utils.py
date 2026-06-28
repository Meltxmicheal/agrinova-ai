from flask_bcrypt import generate_password_hash, check_password_hash
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token
)


class AuthUtils:
    """
    Authentication Utility Class
    Handles password hashing and JWT token generation.
    """

    @staticmethod
    def hash_password(password: str) -> str:
        """
        Hash user password using Bcrypt.
        """
        return generate_password_hash(password).decode("utf-8")

    @staticmethod
    def verify_password(password: str, hashed_password: str) -> bool:
        """
        Verify user password.
        """
        return check_password_hash(hashed_password, password)

    @staticmethod
    def generate_access_token(user):
        """
        Generate JWT Access Token.
        """
        return create_access_token(
            identity=str(user.id),
            additional_claims={
                "email": user.email,
                "full_name": user.full_name
            }
        )

    @staticmethod
    def generate_refresh_token(user):
        """
        Generate JWT Refresh Token.
        """
        return create_refresh_token(
            identity=str(user.id)
        )

    @staticmethod
    def generate_tokens(user):
        """
        Generate both Access and Refresh Tokens.
        """
        return {
            "access_token": AuthUtils.generate_access_token(user),
            "refresh_token": AuthUtils.generate_refresh_token(user)
        }