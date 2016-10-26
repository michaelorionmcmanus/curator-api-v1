from marshmallow_jsonapi import Schema, fields

# JSONAPI Schema
class AccountSchema(Schema):
    id = fields.Str(dump_only=True)
    name = fields.Str()
    created = fields.DateTime()
    owners = fields.List(fields.Str())
    members = fields.List(fields.Str())

    class Meta:
        type_ = 'accounts'
        strict = True