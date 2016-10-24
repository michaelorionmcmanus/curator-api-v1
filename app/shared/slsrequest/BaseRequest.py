from os.path import dirname, basename, isfile
import glob
import os
import sys
here = os.path.dirname(os.path.realpath(__file__))
modelsDir = os.path.join(here, "../../models")
sys.path = [modelsDir] + sys.path
sys.path = [os.path.join(here, "../../")] + sys.path

import logging
import json
from flywheel import Model, Field, Engine
from models import *

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
        # Create an engine and connect to an AWS region
        engine = Engine()
        if('USE_LOCAL_DB' in os.environ and os.environ['USE_LOCAL_DB'] == 'True'):
            engine.connect('us-west-2', host='localhost',
                port=8000,
                access_key='anything',
                secret_key='anything',
                is_secure=False)
        else:
            engine.connect_to_region('us-west-2')
        # auto-magically load and register dynamo db models
        modelModules = glob.glob(modelsDir+"/*.py")
        models = [ basename(f)[:-3] for f in modelModules if isfile(f)]
        for modelName in models:
            if modelName != '__init__':
                engine.register(getattr(__import__(modelName), modelName))
        # Now attach the dynamo db engine for use
        self.db = engine

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