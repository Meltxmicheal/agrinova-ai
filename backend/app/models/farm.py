import uuid
from datetime import datetime

from app.extensions import db


class Farm(db.Model):
    """
    Farm Model
    Stores farm information for each user.
    """

    __tablename__ = "farms"

    id = db.Column(
        db.String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4())
    )

    user_id = db.Column(
        db.String(36),
        db.ForeignKey("users.id"),
        nullable=False
    )

    farm_name = db.Column(
        db.String(100),
        nullable=False
    )

    country = db.Column(
        db.String(100),
        nullable=True
    )

    state = db.Column(
        db.String(100),
        nullable=True
    )

    district = db.Column(
        db.String(100),
        nullable=True
    )

    taluk = db.Column(
        db.String(100),
        nullable=True
    )

    village = db.Column(
        db.String(100),
        nullable=False
    )

    soil_type = db.Column(
        db.String(100),
        nullable=False
    )

    farm_size = db.Column(
        db.Float,
        nullable=False
    )

    latitude = db.Column(
        db.Float,
        nullable=True
    )

    longitude = db.Column(
        db.Float,
        nullable=True
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    owner = db.relationship(
        "User",
        backref=db.backref("farms", cascade="all, delete-orphan"),
        lazy=True
    )

    def __repr__(self):
        return f"<Farm {self.farm_name}>"