from slsrequest import BaseRequest
import json, requests, arrow, uuid
from Account import Account
from serializers import AccountSchema

class AccountsController(BaseRequest):
    def __init__(self, event, context):
        BaseRequest.__init__(self, event, context)
        self.log('Initialized AccountsManager instance')

    # Return all accounts for owner
    def get_handler(self, event, context, principal_id):
        ownedAccounts = self.db.scan(Account).filter(Account.owners.contains_(principal_id)).all()
        accounts = []
        account_schema = AccountSchema()
        for account in ownedAccounts:
            accounts.append(account)
        return { 'body': account_schema.dump(accounts, True).data}

    # Create an account
    def post_handler(self, event, context, principal_id):
        name = event['body']['name']
        account = Account(name, uuid.uuid4().__str__(), principal_id)
        self.db.sync(account)
        account_schema = AccountSchema()
        return { 
            'statusCode': 201,
            'body': account_schema.dump(account.__json__()).data
        }

def handler(event, context):
    SlsRequestInstance = AccountsController(event, context)
    return SlsRequestInstance.handler(event=event, context=context)