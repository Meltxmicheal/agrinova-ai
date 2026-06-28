from marshmallow import Schema, fields, validates, ValidationError


class FertilizerRecommendationSchema(Schema):
    """
    Fertilizer Recommendation Query Validation Schema
    """

    farm_id = fields.String(required=True)
    crop_type = fields.String(required=True)
    season = fields.String(required=False, allow_none=True)
    farming_goal = fields.String(required=False, allow_none=True)
