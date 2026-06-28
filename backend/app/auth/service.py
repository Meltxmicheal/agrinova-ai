from app.models.user import User
from app.extensions import db, bcrypt


class AuthService:
    @staticmethod
    def register(data):
        """
        Register a new user.
        """

        try:
            # Check if email already exists
            existing_email = User.query.filter_by(email=data["email"]).first()
            if existing_email:
                return {
                    "success": False,
                    "message": "Email is already registered."
                }, 409

            # Check if phone already exists
            existing_phone = User.query.filter_by(phone=data["phone"]).first()
            if existing_phone:
                return {
                    "success": False,
                    "message": "Phone number is already registered."
                }, 409

            # Hash password
            hashed_password = bcrypt.generate_password_hash(
                data["password"]
            ).decode("utf-8")

            # Create user object
            user = User(
                full_name=data["full_name"],
                email=data["email"],
                phone=data["phone"],
                password_hash=hashed_password
            )

            # Save user to database
            db.session.add(user)
            db.session.commit()

            return {
                "success": True,
                "message": "Account created successfully.",
                "user": {
                    "id": user.id,
                    "full_name": user.full_name,
                    "email": user.email,
                    "phone": user.phone,
                    "is_verified": user.is_verified,
                    "created_at": user.created_at.isoformat()
                }
            }, 201

        except Exception as e:
            # Rollback database transaction
            db.session.rollback()

            return {
                "success": False,
                "message": "An unexpected error occurred.",
                "error": str(e)
            }, 500