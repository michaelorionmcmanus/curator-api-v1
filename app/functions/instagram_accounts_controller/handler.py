import os, requests
from apiclients import InstagramClient
from ...serializers import InstagramAccountSchema
from ...models.AccountCredential import AccountCredential
import tight.providers.aws.controllers.lambda_proxy_event as lambda_proxy
from tight.providers.aws.clients import dynamo_db
instagram_client = InstagramClient()
db = dynamo_db.connect()

def persist_credential(channel, account_id, instagram_account_id, access_token, account_info):
    existing = db.query(AccountCredential).filter(AccountCredential.channel==channel, AccountCredential.account_id==account_id).first()
    if existing:
        raise Exception({
            "statusCode": 400,
            "body": {
                "errors": [{
                    "data": {
                        "instagram_account_username": account_info['username']
                    },
                    'message': 'Account is already authorized'
                }]
            }
        })
    credentials ={
        'user_id': instagram_account_id,
        'access_token': access_token
    }
    new_credential = AccountCredential(channel, account_id, credentials)
    db.sync(new_credential)


def get_instagram_account_credentials(code, redirect_uri):
    try:
        r = requests.post('https://api.instagram.com/oauth/access_token', data = {
                'client_id': os.environ.get('INSTAGRAM_CLIENT_ID'),
                'client_secret': os.environ.get('INSTAGRAM_CLIENT_SECRET'),
                'grant_type': 'authorization_code',
                'redirect_uri': redirect_uri,
                'code': code,
            })
    except Exception as e:
        raise Exception({
            "statusCode": 500,
            "body": {
                "errors": [{
                    "message": 'Sorry. Something went very, very wrong.'
                }]
            }
        })
    status = r.status_code
    if status == 200:
        response_body = r.json()
        access_token = response_body['access_token']
        account_info = response_body['user']
    elif status == 400:
        response_body = r.json()
        raise Exception({
            "statusCode": 400,
            "body": {
                "errors": [{
                    "data": {
                        "error_type": response_body['error_type']
                    },
                    "message": response_body['error_message']
                }]
            }
        })
    return {'access_token': access_token, 'account_info': account_info}


def authorize_account(event):
    account_id = event['pathParameters']['accountId']
    code = event['body']['data']['attributes']['code']
    redirect_uri = event['body']['data']['attributes']['redirect-uri']
    credentials = get_instagram_account_credentials(code, redirect_uri)
    account_info = credentials['account_info']
    access_token = credentials['access_token']
    instagram_account_id = account_info['id']
    channel = 'instagram:' + instagram_account_id
    persist_credential(channel, account_id, instagram_account_id, access_token, account_info)
    account_info['profile-picture'] = account_info['profile_picture']
    account_info['full-name'] = account_info['full_name']
    account_info.pop('profile_picture')
    account_info.pop('full_name')
    instagram_account = {
        "id": account_info['id'],
        "type": 'instagram-account',
        "attributes": account_info
    }
    return {
        'statusCode': 201,
        'body': {
            "data": instagram_account
        }
    }


@lambda_proxy.get
def get_handler(*args, **kwargs):
    event = kwargs.pop('event')
    account_id = event['pathParameters']['accountId']
    credentials = db.query(AccountCredential).filter(AccountCredential.account_id == account_id, AccountCredential.channel.beginswith_('instagram')).all()
    instagram_accounts_schema = InstagramAccountSchema()
    accounts = []
    for item in credentials:
        access_token = item.credentials['access_token']
        account_details = instagram_client.get_user(access_token=access_token)
        accounts.append(account_details.__dict__)
    return { 'body': instagram_accounts_schema.dump(accounts, True).data}


@lambda_proxy.post
def post_handler(*args, **kwargs):
    event = kwargs.pop('event')
    return authorize_account(event)