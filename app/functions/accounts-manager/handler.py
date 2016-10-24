import sys, os
here = os.path.dirname(os.path.realpath(__file__))
sys.path = [os.path.join(here, "../../vendored")] + sys.path
sys.path = [os.path.join(here, "../../shared")] + sys.path
sys.path = [os.path.join(here, "../../models")] + sys.path

from slsrequest import BaseRequest
import json
import requests
import arrow
import uuid
from Account import Account
from serializers import AccountSchema

class AccountsManager(BaseRequest):
    def __init__(self):
        BaseRequest.__init__(self)
        self.log('Initialized AccountsManager instance')

    def get_handler(self, event, context):
        # query the database for all accounts owned by the requesting user
        accountModels = self.db \
            .query(Account) \
            .filter(Account.owner_id == '1') \
            .index('created-index') \
            .limit(10) \
            .all(desc=True)

        accounts = []
        account_schema = AccountSchema()
        for account in accountModels:
            accounts.append(account.__json__())
        return { 'body': json.dumps(account_schema.dump(accounts, True).data)}

    def post_handler(self, event, context):
        name = event['body']['name']
        account = Account(name, uuid.uuid4().__str__(), '1', arrow.utcnow().datetime)
        self.db.sync(account)
        account_schema = AccountSchema()
        return { 
            'statusCode': 201,
            'body': account_schema.dump(account.__json__()).data
        }

def handler(event, context):
    SlsRequestInstance = AccountsManager()
    return SlsRequestInstance.handler(event=event, context=context)