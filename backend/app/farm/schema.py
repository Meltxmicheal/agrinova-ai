from marshmallow import Schema, fields, validates, ValidationError


class FarmSchema(Schema):
    """
    Farm Validation Schema
    """

    farm_name = fields.String(required=True)
    country = fields.String(required=False, allow_none=True)
    state = fields.String(required=False, allow_none=True)
    district = fields.String(required=False, allow_none=True)
    taluk = fields.String(required=False, allow_none=True)
    village = fields.String(required=True)
    soil_type = fields.String(required=True)
    farm_size = fields.Float(required=True)
    latitude = fields.Float(required=False, allow_none=True)
    longitude = fields.Float(required=False, allow_none=True)

    @validates("farm_name")
    def validate_farm_name(self, value, **kwargs):
        if len(value.strip()) < 3:
            raise ValidationError(
                "Farm name must contain at least 3 characters."
            )

    @validates("farm_size")
    def validate_farm_size(self, value, **kwargs):
        if value <= 0:
            raise ValidationError(
                "Farm size must be greater than 0."
            )