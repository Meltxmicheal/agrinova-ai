from marshmallow import Schema, fields


class DiseaseResponseSchema(Schema):
    """
    Disease Detection Output Response Schema
    """

    success = fields.Boolean()
    prediction_id = fields.String()
    crop = fields.String()
    disease = fields.String()
    healthy = fields.Boolean()
    confidence = fields.Float()
    recommendation = fields.String()
    created_at = fields.String()
