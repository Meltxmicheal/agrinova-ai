from app.models.user import User
from app.extensions import db, bcrypt


def register_user(data):

    hashed_password = bcrypt.generate_password_hash(
        data["password"]
    ).decode("utf-8")

    user = User(
        full_name=data["full_name"],
        email=data["email"],
        phone=data["phone"],
        password_hash=hashed_password
    )

    db.session.add(user)
    db.session.commit()

    return user