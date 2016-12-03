from slsrequest import BaseRequest
import json, requests, arrow, uuid, re, os, boto3
from shared.pubsub import client as pubsub
from Account import Account
from AccountUser import AccountUser 
from serializers import AccountSchema

region = os.environ['SERVERLESS_REGION']
iot_client = boto3.client('iot', region_name=region)
cognito_idp_client= boto3.client('cognito-idp', region_name=region)
default_iot_policy_name = '{}-{}-user-v2'.format(os.environ['SERVERLESS_SERVICE_NAME'], os.environ['STAGE'])

# pubsub_client = pubsub.get_client()

class UsersController(BaseRequest):
    def __init__(self, event, context):
        BaseRequest.__init__(self, event, context)
        self.log('Initialized UsersController instance')

    def add_cognito_identity_claim_value(self, event, context, identity):
        username = event['requestContext']['authorizer']['claims']['cognito:username']
        iss = event['requestContext']['authorizer']['claims']['iss']
        user_pool_id = iss.split('/')[-1]
        try:
            user = cognito_idp_client.admin_get_user(UserPoolId=user_pool_id, Username=username)
            user_exists = True
            self.log('User exists!')
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
                self.log('User does not exist.')
            else:
                raise e

    def grant_iot_access(self, identity, event, context):
        response = iot_client.attach_principal_policy(
            policyName=default_iot_policy_name,
            principal=identity
        )
        self.add_cognito_identity_claim_value(event, context, identity)

    def add_cognito_identities(self, path_parts, value, event, context):
        principal_policies = iot_client.list_principal_policies(principal = value, pageSize = 50)
        if len(principal_policies['policies']) > 0:
            policy_names = [item['policyName'] for item in principal_policies['policies']]
            if default_iot_policy_name not in policy_names:
                self.log('{} not found'.format(default_iot_policy_name))
                self.grant_iot_access(value, event, context)
            else:
                self.log('Has {}'.format(default_iot_policy_name))
        else:
            self.grant_iot_access(value, event, context)
        
        

    def patch_handler(self, event, context, principal_id):
        # For each operation call the method that matches the operation method 
        # and attribute. For example, the following patch operation:
        # {"op": "add", "path": "/some-attribute/1", "value": "some value"}
        # would result in a call to self.add_some_attribute()
        for operation in event['body']:
            pattern = re.compile('/(.*)/(.*)')
            method = operation['op']
            path_parts = operation['path'].split('/')
            attribute = path_parts[1]
            value = operation['value']
            getattr(self, '{}_{}'.format(method, attribute.replace('-', '_')))(path_parts, value, event, context)

        return {
            'statusCode': 204,
            'body': {}
        }

    def post_handler(self, event, context, principal_id):
        pubsub_client.publish('us-west-2:f3889f42-8f28-421d-b476-1e5039476414', 'HAI', 1)
        return {
            'statusCode': 201,
            'body': {}
        }

def handler(event, context):
    SlsRequestInstance = UsersController(event, context)
    return SlsRequestInstance.handler(event=event, context=context)