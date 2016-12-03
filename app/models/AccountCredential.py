from flywheel import Model, Field, Engine, GlobalIndex
from datetime import datetime
import arrow
import os 

# DynamoDB Model
class AccountCredential(Model):
    __metadata__ = {
        '_name': 'curator-v1-%s-account-credentials' % os.environ['STAGE'],
        'global_indexes': [
            GlobalIndex.all('account-index', 'account_id', 'channel').throughput(read=1, write=1),
        ],
        'throughput': {
            'read': 1,
            'write': 1
        }
    }

    channel = Field(type=unicode, hash_key=True)
    account_id = Field(type=unicode, range_key=True)
    credentials = Field(type=dict, coerce=True)
    updated = Field(type=datetime, index='updated-index')

    # Constructor
    def __init__(self, channel, account_id, credentials):
        self.channel = channel
        self.account_id = account_id
        self.credentials = credentials
        self.updated = arrow.utcnow().datetime