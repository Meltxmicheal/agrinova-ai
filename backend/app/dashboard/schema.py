from marshmallow import Schema, fields


class DashboardStatsSchema(Schema):
    """
    Dashboard Stats Response Schema
    """

    farms_count = fields.Integer()
    total_size_hectares = fields.Float()
    predictions_count = fields.Integer()
    breakdown = fields.Dict(keys=fields.Str(), values=fields.Int())
