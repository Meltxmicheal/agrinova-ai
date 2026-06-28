from marshmallow import Schema, fields


class WeatherQuerySchema(Schema):
    """
    Weather Query Schema
    Validates incoming weather retrieval requests.
    """

    farm_id = fields.String(required=True)
