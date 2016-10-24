from marshmallow_jsonapi import Schema, fields

# JSONAPI Schema
class AccountSchema(Schema):
    id = fields.Str(dump_only=True)
    name = fields.Str()
    created = fields.Str()
    owner_id = fields.Str()

    class Meta:
        type_ = 'accounts'
        strict = True