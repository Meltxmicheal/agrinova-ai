from marshmallow import Schema, fields, validates, ValidationError


class CropRecommendationSchema(Schema):
    """
    Crop Recommendation Input Validation Schema
    """

    farm_id = fields.String(required=True)
    season = fields.String(required=True)
    farming_goal = fields.String(required=False, allow_none=True)
