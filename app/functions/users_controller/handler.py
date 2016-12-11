import json, sys, re, os
import tight.providers.aws.controllers.lambda_proxy_event as lambda_proxy
from tight.core.logger import info
from tight.providers.aws.clients.boto3_client import session

boto3_client = session()
region = os.environ['SERVERLESS_REGION']
iot_client = boto3_client.client('iot', region_name=region)
cognito_idp_client= boto3_client.client('cognito-idp', region_name=region)
default_iot_policy_name = '{}-{}-user-v2'.format(os.environ['SERVERLESS_SERVICE_NAME'], os.environ['STAGE'])

def add_cognito_identity_claim_value(event, context, identity):
    username = event['requestContext']['authorizer']['claims']['cognito:username']
    iss = event['requestContext']['authorizer']['claims']['iss']
    user_pool_id = iss.split('/')[-1]
    try:
        user = cognito_idp_client.admin_get_user(UserPoolId=user_pool_id, Username=username)
        user_exists = True
        info(message='User exists!')
        identities = [identity]
        for attribute in user['UserAttributes']:
            if attribute['Name'] == 'custom:cognitoIdentities':
                cognitoidentities = attribute['Value']

        if 'cognitoidentities' in locals():
            existing_identities = json.loads(cognitoidentities)
            identities = identities + existing_identities
        # Remove dupes
        identities = list(set(identities))
        cognito_idp_client.admin_update_user_attributes(UserPoolId=user_pool_id, Username=username,
            UserAttributes=[
                {
                    'Name': 'custom:cognitoIdentities',
                    'Value': json.dumps(identities)
                },
        ])
    except Exception as e:
        if (e.response['Error']['Code'] == 'UserNotFoundException'):
            info(message='User does not exist.')
        else:
            raise e

def grant_iot_access(identity, event, context):
    response = iot_client.attach_principal_policy(
        policyName=default_iot_policy_name,
        principal=identity
    )
    add_cognito_identity_claim_value(event, context, identity)

def add_cognito_identities(path_parts, value, event, context):
    info(message='A')
    principal_policies = iot_client.list_principal_policies(principal = value, pageSize = 50)
    if len(principal_policies['policies']) > 0:
        policy_names = [item['policyName'] for item in principal_policies['policies']]
        if default_iot_policy_name not in policy_names:
            info(message='{} not found'.format(default_iot_policy_name))
            grant_iot_access(value, event, context)
        else:
            info(message='Has {}'.format(default_iot_policy_name))
    else:
        grant_iot_access(value, event, context)

@lambda_proxy.patch
def patch_handler(*args, **kwargs):
    # For each operation call the method that matches the operation method
    # and attribute. For example, the following patch operation:
    # {"op": "add", "path": "/some-attribute/1", "value": "some value"}
    # would result in a call to add_some_attribute()
    event = kwargs.pop('event')
    context = kwargs.pop('context')
    for operation in event['body']:
        pattern = re.compile('/(.*)/(.*)')
        method = operation['op']
        path_parts = operation['path'].split('/')
        attribute = path_parts[1]
        value = operation['value']
        getattr(sys.modules[__name__], '{}_{}'.format(method, attribute.replace('-', '_')))(path_parts, value, event, context)

    return {
        'statusCode': 204,
        'body': {}
    }