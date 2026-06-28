from marshmallow import Schema, fields, validates, ValidationError
import re


class RegisterSchema(Schema):
    full_name = fields.String(required=True)
    email = fields.Email(required=True)
    phone = fields.String(required=True)
    password = fields.String(required=True)
    confirm_password = fields.String(required=True)

    @validates("full_name")
    def validate_name(self, value, **kwargs):
        if len(value.strip()) < 3:
            raise ValidationError("Full name must contain at least 3 characters.")

    @validates("phone")
    def validate_phone(self, value, **kwargs):
        if not re.fullmatch(r"\d{10}", value):
            raise ValidationError("Phone number must contain exactly 10 digits.")

    @validates("password")
    def validate_password(self, value, **kwargs):
        if len(value) < 8:
            raise ValidationError("Password must be at least 8 characters long.")

        if not re.search(r"[A-Z]", value):
            raise ValidationError("Password must contain at least one uppercase letter.")

        if not re.search(r"[a-z]", value):
            raise ValidationError("Password must contain at least one lowercase letter.")

        if not re.search(r"\d", value):
            raise ValidationError("Password must contain at least one number.")

        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", value):
            raise ValidationError("Password must contain at least one special character.")

    def validate_confirm_password(self, data):
        if data["password"] != data["confirm_password"]:
            raise ValidationError("Passwords do not match.")