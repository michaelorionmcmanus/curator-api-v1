from flywheel import Model, Field, Engine
from datetime import datetime
import arrow

# DynamoDB Model
class AccountUser(Model):
    __metadata__ = {
        #TODO This needs to come from env settings
        '_name': 'curator-v1-dev-accounts-users',
    }
    user_id = Field(type=unicode, hash_key=True)
    account_id = Field(type=unicode, range_key=True)
    access = Field(type=unicode)
    created = Field(type=datetime)

    # Constructor
    def __init__(self, user_id, account_id, access):
        self.user_id = user_id
        self.account_id = account_id
        self.access = access
        self.created = arrow.utcnow().datetime