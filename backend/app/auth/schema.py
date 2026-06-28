from marshmallow import Schema, fields, validates, ValidationError
import re


class RegisterSchema(Schema):
    """
    User Registration Schema
    """

    full_name = fields.String(required=True)
    email = fields.Email(required=True)
    phone = fields.String(required=True)
    password = fields.String(required=True)
    confirm_password = fields.String(required=True)

    @validates("full_name")
    def validate_name(self, value, **kwargs):
        if len(value.strip()) < 3:
            raise ValidationError(
                "Full name must contain at least 3 characters."
            )

        if len(value.strip()) > 100:
            raise ValidationError(
                "Full name cannot exceed 100 characters."
            )

    @validates("phone")
    def validate_phone(self, value, **kwargs):
        if not re.fullmatch(r"\d{10}", value):
            raise ValidationError(
                "Phone number must contain exactly 10 digits."
            )

    @validates("password")
    def validate_password(self, value, **kwargs):

        if len(value) < 8:
            raise ValidationError(
                "Password must be at least 8 characters long."
            )

        if not re.search(r"[A-Z]", value):
            raise ValidationError(
                "Password must contain at least one uppercase letter."
            )

        if not re.search(r"[a-z]", value):
            raise ValidationError(
                "Password must contain at least one lowercase letter."
            )

        if not re.search(r"\d", value):
            raise ValidationError(
                "Password must contain at least one number."
            )

        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", value):
            raise ValidationError(
                "Password must contain at least one special character."
            )

    @validates("confirm_password")
    def validate_confirm_password(self, value, **kwargs):
        if len(value) < 8:
            raise ValidationError(
                "Confirm Password must be at least 8 characters long."
            )


class LoginSchema(Schema):
    """
    User Login Schema
    """

    email = fields.Email(
        required=True,
        error_messages={
            "required": "Email is required.",
            "invalid": "Invalid email address."
        }
    )

    password = fields.String(
        required=True,
        error_messages={
            "required": "Password is required."
        }
    )