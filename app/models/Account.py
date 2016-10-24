from flywheel import Model, Field, Engine
from datetime import datetime

# DynamoDB Model
class Account(Model):
    __metadata__ = {
        #TODO This needs to come from env settings
        '_name': 'curator-v1-dev-accounts',
    }
    owner_id = Field(type=unicode, hash_key=True)
    id = Field(type=unicode, range_key=True)
    name = Field(type=unicode)
    created = Field(type=datetime, index='created-index')

    # Constructor
    def __init__(self, name, id, owner_id, created):
        self.name = name
        self.id = id
        self.owner_id = owner_id
        self.created = created