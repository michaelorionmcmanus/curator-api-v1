import os
import logging
import json

class BaseRequest(object):
    _methods = {
        "POST": "post_handler",
        "OPTIONS": "options_handler",
        "GET": "get_handler",
        "DELETE": "delete_handler",
        "PATCH": "patch_handler"
    }

    def __init__(self):
        logging.basicConfig()
        self.logger = logging.getLogger()
        self.logger.setLevel(logging.INFO)

        # SERVERLESS_PROJECT_NAME = os.environ.get('SERVERLESS_PROJECT')
        # SERVERLESS_STAGE = os.environ.get('SERVERLESS_STAGE')
        # CREDENTIALS_TABLE = '-'.join([SERVERLESS_STAGE, SERVERLESS_PROJECT_NAME, 'credentials'])
        # ACCOUNTS_TABLE = '-'.join([SERVERLESS_STAGE, SERVERLESS_PROJECT_NAME, 'accounts'])
        # USERS_ACCOUNTS_TABLE = '-'.join([SERVERLESS_STAGE, SERVERLESS_PROJECT_NAME, 'users', 'accounts'])
        # AAD_USERS_TABLE = '-'.join([SERVERLESS_STAGE, SERVERLESS_PROJECT_NAME, 'aad', 'users'])
        # SYSTEM_BUCKET = '-'.join([SERVERLESS_STAGE, SERVERLESS_PROJECT_NAME, 'system'])
        # # It might be better to just inject these "computed" env vars as global env vars... it feels
        # # a little funny that there are multiple ways to access "environment variables"
        # self.env = {
        #     "SERVERLESS_PROJECT_NAME": SERVERLESS_PROJECT_NAME,
        #     "SERVERLESS_STAGE": SERVERLESS_STAGE,
        #     "CREDENTIALS_TABLE": CREDENTIALS_TABLE,
        #     "ACCOUNTS_TABLE": ACCOUNTS_TABLE,
        #     "USERS_ACCOUNTS_TABLE": USERS_ACCOUNTS_TABLE,
        #     "AAD_USERS_TABLE": AAD_USERS_TABLE,
        #     "SYSTEM_BUCKET": SYSTEM_BUCKET
        # }

    def log(self, message):
        self.logger.info(message)

    def options_handler(self, event, context):
        return None

    def handler(self, event, context):
        self.log(json.dumps(event))
        self.log('RECEIVED EVENT')
        try:
            method_name = self._methods[event["httpMethod"]]
            self.log('calling' + method_name)
            response = getattr(self, '%s' % method_name)(event, context)
        except Exception as e:
            # TODO handle other exception types.
            self.log(e)

            if type(e.message) is dict:
                raise Exception(json.dumps(e.message))
            else:
                raise Exception(json.dumps({
                    'statusCode': '500',
                    'body': {
                        'errors': [str(e)]
                    }
                }))

        if('body' not in response):
            response['body'] = {}
        
        if('statusCode' not in response):
            response['statusCode'] = 200
        
        if('headers' not in response):
            response['headers'] = {
                'Access-Control-Allow-Origin': '*'
            }
            
        return response