from flywheel import Model, Field, Engine
from datetime import datetime
import arrow
import os 

# DynamoDB Model
class Account(Model):
    __metadata__ = {
        '_name': 'curator-v1-%s-accounts' % os.environ['STAGE']
    }

    id = Field(type=unicode, hash_key=True)
    name = Field(type=unicode, range_key=True)
    owners = Field(type=set, coerce=True)
    members = Field(type=set, coerce=True)
    created = Field(type=datetime, index='created-index')

    # Constructor
    def __init__(self, name, id, owner_id):
        self.name = name
        self.id = id
        self.owners = set([owner_id])
        self.members = set()
        self.created = arrow.utcnow().datetime