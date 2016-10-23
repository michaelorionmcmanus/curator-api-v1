import sys, os
here = os.path.dirname(os.path.realpath(__file__))
sys.path = [os.path.join(here, "../../vendored")] + sys.path
sys.path = [os.path.join(here, "../../shared")] + sys.path

from slsrequest import BaseRequest
import json
import requests

class AccountsManager(BaseRequest):
    def __init__(self):
        BaseRequest.__init__(self)
        self.log('Initialized AccountsManager instance')
        # self.accounts_table = boto3.resource('dynamodb', region_name='us-west-2').Table(self.env['ACCOUNTS_TABLE'])
        # self.users_accounts_table = boto3.resource('dynamodb', region_name='us-west-2').Table(self.env['USERS_ACCOUNTS_TABLE'])
        # self.json_api_util = JSONApi()
        # self.auth0_client = AuthClient()

    def get_handler(self, event, context):
        return { 'body': json.dumps(event) }

def handler(event, context):
    SlsRequestInstance = AccountsManager()
    return SlsRequestInstance.handler(event=event, context=context)

# def handler(event, context):

#     body = {
#         "message": "Go Serverless v1.0! Your function executed successfully!",
#         "input": event
#     }

#     response = {
#         "statusCode": 200,
#         "body": json.dumps(body)
#     };

#     return response