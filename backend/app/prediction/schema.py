from marshmallow import Schema, fields, validates, ValidationError


class YieldPredictionSchema(Schema):
    """
    Yield Prediction Input Validation Schema
    """

    farm_id = fields.String(required=True)
    crop = fields.String(required=True)
    season = fields.String(required=True)


class PricePredictionSchema(Schema):
    """
    Market Price Prediction Input Validation Schema
    """

    farm_id = fields.String(required=True)
    commodity = fields.String(required=True)
    month = fields.Integer(required=True)

    @validates("month")
    def validate_month(self, value, **kwargs):
        if value < 1 or value > 12:
            raise ValidationError("Month must be an integer between 1 and 12.")
