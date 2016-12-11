import uuid
from Account import Account
from AccountUser import AccountUser
from AccountSchema import AccountSchema
from tight.providers.aws.clients import dynamo_db
import tight.providers.aws.controllers.lambda_proxy_event as lambda_proxy
db = dynamo_db.connect()

@lambda_proxy.get
def get_method(*args, **kwargs):
    principal_id = kwargs.pop('principal_id', None)
    user_accounts = db.query(AccountUser).filter(user_id=principal_id).all()
    owned_accounts = []
    for item in user_accounts:
        if(item.access == 'owner'):
            owned_accounts.append(db.query(Account).filter(id=item.account_id).first())
    account_schema = AccountSchema()
    return { 'body': account_schema.dump(owned_accounts, True).data}

@lambda_proxy.post
def post_handler(*args, **kwargs):
    principal_id = kwargs.pop('principal_id', None)
    event = kwargs.pop('event')
    account_schema = AccountSchema()
    new_account = account_schema.load(event['body'] or {})
    name = new_account.data['name']
    account = Account(name, uuid.uuid4().__str__(), principal_id)
    account_user = AccountUser(principal_id, account.id, 'owner')
    db.sync(account)
    db.sync(account_user)
    account_schema = AccountSchema()
    return {
        'statusCode': 201,
        'body': account_schema.dump(account).data
    }