from app.models.user import User
from app.auth.repository import AuthRepository
from app.auth.utils import AuthUtils


class AuthService:
    """
    Authentication Service
    Handles all business logic related to authentication.
    """

    @staticmethod
    def register(data):
        """
        Register a new user.
        """

        try:
            # Check if email already exists
            existing_email = AuthRepository.get_user_by_email(data["email"])
            if existing_email:
                return {
                    "success": False,
                    "message": "Email is already registered."
                }, 409

            # Check if phone already exists
            existing_phone = AuthRepository.get_user_by_phone(data["phone"])
            if existing_phone:
                return {
                    "success": False,
                    "message": "Phone number is already registered."
                }, 409

            # Hash password
            hashed_password = AuthUtils.hash_password(data["password"])

            # Create User Object
            user = User(
                full_name=data["full_name"],
                email=data["email"],
                phone=data["phone"],
                password_hash=hashed_password
            )

            # Save user
            AuthRepository.create_user(user)

            return {
                "success": True,
                "message": "Account created successfully.",
                "user": {
                    "id": str(user.id),
                    "full_name": user.full_name,
                    "email": user.email,
                    "phone": user.phone,
                    "is_verified": user.is_verified,
                    "created_at": (
                        user.created_at.isoformat()
                        if user.created_at
                        else None
                    )
                }
            }, 201

        except Exception as e:

            AuthRepository.rollback()

            return {
                "success": False,
                "message": "An unexpected error occurred while creating the account.",
                "error": str(e)
            }, 500

    @staticmethod
    def login(data):
        """
        Authenticate user and generate JWT tokens.
        """

        try:

            # Find user by email
            user = AuthRepository.get_user_by_email(data["email"])

            if not user:
                return {
                    "success": False,
                    "message": "Invalid email or password."
                }, 401

            # Verify Password
            if not AuthUtils.verify_password(
                data["password"],
                user.password_hash
            ):
                return {
                    "success": False,
                    "message": "Invalid email or password."
                }, 401

            # Generate Access & Refresh Tokens
            tokens = AuthUtils.generate_tokens(user)

            return {
                "success": True,
                "message": "Login successful.",
                "access_token": tokens["access_token"],
                "refresh_token": tokens["refresh_token"],
                "user": {
                    "id": str(user.id),
                    "full_name": user.full_name,
                    "email": user.email,
                    "phone": user.phone,
                    "is_verified": user.is_verified,
                    "created_at": (
                        user.created_at.isoformat()
                        if user.created_at
                        else None
                    )
                }
            }, 200

        except Exception as e:

            return {
                "success": False,
                "message": "An unexpected error occurred during login.",
                "error": str(e)
            }, 500

    @staticmethod
    def refresh_token(user_id):
        """
        Refresh access token using valid refresh token.
        """
        try:
            user = AuthRepository.get_user_by_id(user_id)
            if not user:
                return {
                    "success": False,
                    "message": "User not found."
                }, 404

            # Generate new access token
            access_token = AuthUtils.generate_access_token(user)
            return {
                "success": True,
                "access_token": access_token
            }, 200

        except Exception as e:
            return {
                "success": False,
                "message": "Failed to refresh token.",
                "error": str(e)
            }, 500

    @staticmethod
    def forgot_password(email):
        """
        Generate password reset token and log/return it.
        """
        try:
            user = AuthRepository.get_user_by_email(email)
            if not user:
                # Return success for security, but indicate a mock link
                return {
                    "success": True,
                    "message": "If the email is registered, a password reset token has been generated."
                }, 200

            # Generate short-lived reset token (15 mins)
            from flask_jwt_extended import create_access_token
            import datetime
            reset_token = create_access_token(
                identity=str(user.id),
                expires_delta=datetime.timedelta(minutes=15),
                additional_claims={"purpose": "password_reset"}
            )

            # In a production app, we would send this token in an email link.
            # Print to stdout/logs for accessibility, and return in response for dev integration.
            print(f"\n[DEV MODE] Password reset token for {email}: {reset_token}\n")

            return {
                "success": True,
                "message": "Password reset token generated successfully.",
                "token": reset_token
            }, 200

        except Exception as e:
            return {
                "success": False,
                "message": "Failed to generate password reset token.",
                "error": str(e)
            }, 500

    @staticmethod
    def reset_password(token, new_password):
        """
        Reset user password using token.
        """
        try:
            from flask_jwt_extended import decode_token
            
            # Decode and verify token signature/expiration
            try:
                decoded = decode_token(token)
            except Exception:
                return {
                    "success": False,
                    "message": "Invalid or expired reset token."
                }, 400

            # Extract user_id from sub
            user_id = decoded.get("sub")
            
            user = AuthRepository.get_user_by_id(user_id)
            if not user:
                return {
                    "success": False,
                    "message": "User not found."
                }, 404

            # Update password hash
            user.password_hash = AuthUtils.hash_password(new_password)
            AuthRepository.update_user()

            return {
                "success": True,
                "message": "Password has been reset successfully."
            }, 200

        except Exception as e:
            AuthRepository.rollback()
            return {
                "success": False,
                "message": "Failed to reset password.",
                "error": str(e)
            }, 500