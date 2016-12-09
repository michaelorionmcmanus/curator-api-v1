from slsrequest import BaseRequest
import uuid
from ...models.Account import Account
from ...models.AccountUser import AccountUser
from ...serializers import AccountSchema

class AccountsController(BaseRequest):
    def __init__(self, event, context, **kwargs):
        BaseRequest.__init__(self, event, context, **kwargs)
        self.log('Initialized AccountsController instance')

    # Return all accounts for owner
    def get_handler(self, event, context, principal_id):
        user_accounts = self.db.query(AccountUser).filter(user_id=principal_id).all()
        owned_accounts = []
        for item in user_accounts:
            if(item.access == 'owner'):
                owned_accounts.append(self.db.query(Account).filter(id=item.account_id).first())
        account_schema = AccountSchema()
        return { 'body': account_schema.dump(owned_accounts, True).data}

    # Create an account
    def post_handler(self, event, context, principal_id):
        account_schema = AccountSchema()
        new_account = account_schema.load(event['body'])
        name = new_account.data['name']
        account = Account(name, uuid.uuid4().__str__(), principal_id)
        account_user = AccountUser(principal_id, account.id, 'owner')
        self.db.sync(account)
        self.db.sync(account_user)
        account_schema = AccountSchema()
        return {
            'statusCode': 201,
            'body': account_schema.dump(account).data
        }

def handler(*args, **kwargs):
    event, context = args
    SlsRequestInstance = AccountsController(event, context, **kwargs)
    return SlsRequestInstance.handler(event=event, context=context)