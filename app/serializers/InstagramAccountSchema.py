from marshmallow_jsonapi import Schema, fields

# JSONAPI Schema
class InstagramAccountSchema(Schema):
    id = fields.Str(dump_only=True)
    username = fields.Str()
    bio = fields.Str()
    website = fields.Str()
    profile_picture = fields.Str(dump_to='profile-picture')
    full_name = fields.Str(dump_to='full-name')

    class Meta:
        type_ = 'instagram-accounts'
        strict = True