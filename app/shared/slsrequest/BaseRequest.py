from os.path import dirname, basename, isfile
import glob, os, sys, logging, json, traceback
from flywheel import Model, Field, Engine

here = os.path.dirname(os.path.realpath(__file__))
modelsDir = os.path.join(here, "../../models")
sys.path = [modelsDir] + sys.path
sys.path = [os.path.join(here, "../../")] + sys.path
from models import *

class BaseRequest(object):
    _methods = {
        "POST": "post_handler",
        "OPTIONS": "options_handler",
        "GET": "get_handler",
        "DELETE": "delete_handler",
        "PATCH": "patch_handler"
    }

    """
    Constructor
    """
    def __init__(self, event={}, context={}, **kwargs):
        if('requestContext' in event and 'stage' in event['requestContext']):
            os.environ['STAGE'] = event['requestContext']['stage']
        session = kwargs.pop('session', None)
        # Build a logger and attach it to the instance.
        logging.basicConfig()
        self.logger = logging.getLogger()
        self.logger.setLevel(logging.INFO)
        # Create a database engine
        engine = Engine()
        # Connect the engine to either a local DynamoDB or a particular region.
        if('USE_LOCAL_DB' in os.environ and os.environ['USE_LOCAL_DB'] == 'True'):
            engine.connect(os.environ['SERVERLESS_REGION'], host='localhost',
                port=8000,
                access_key='anything',
                secret_key='anything',
                is_secure=False,
                session=session)
        elif os.environ['CI'] == 'True':
            engine.connect_to_region(os.environ['SERVERLESS_REGION'], session=session)
        else:
            engine.connect_to_region(os.environ['SERVERLESS_REGION'])
        
        # Auto-magically load and register dynamo db models

        # First grab file names from the models directory.
        modelModules = glob.glob(modelsDir+"/*.py")
        models = [ basename(f)[:-3] for f in modelModules if isfile(f)]
        # Loop over the list of filenames and use the name to discover the associated 
        # class. Register each model class with the database engine.
        for modelName in models:
            if modelName != '__init__':
                engine.register(getattr(__import__(modelName), modelName))
        # Now attach the dynamo db engine for use with this instance.
        self.db = engine

    def log(self, message):
        self.logger.info(message)

    # Options handler returns nada.
    def options_handler(self, event, context):
        return None

    """
    Entry point. 

    The `handler` should be the method invoked when running your lambda. 
    """
    def handler(self, event, context):
        # Dump the event.
        self.log(json.dumps(event))
        self.log('RECEIVED EVENT')
        # Call the appropriate handler for the request method indicated
        # in the event.
        try:
            method_name = self._methods[event["httpMethod"]]
            self.log('calling ' + method_name)
            # Extract body
            if('body' in event and event['body'] != None):
                try:
                    event['body'] = json.loads(event['body'])
                except Exception as e:
                    self.log('Could not json.loads ' + str(event['body']))
                    event['body'] = {}
            try:
                principal_id = event['requestContext']['authorizer']['claims']['sub']
            except Exception as e:
                principal_id = None
            response = getattr(self, '%s' % method_name)(event, context, principal_id)
        # Whoopsie. Something went wrong. This is a catchall for non-handled
        # exceptions. This should be considered a last resort. Catch errors 
        # at the site of the exception.
        except Exception as e:
            # TODO handle other exception types.
            self.log(e)
            if type(e.message) is dict:
                response = e.message
            else:
                traceback.print_exc()
                response = {
                    'statusCode': '500',
                    'body': json.dumps({
                        'errors': [str(e)]
                    })
                }
        if('passthrough' in response):
            return response['passthrough']
        # Map return properties to the response.
        if('body' not in response):
            response['body'] = {}
        elif (not isinstance(response['body'], str)):
            response['body'] = json.dumps(response['body'])
        # Default response code is 200
        if('statusCode' not in response):
            response['statusCode'] = 200
        # Response header needs to specify `Access-Control-Allow-Origin` in order
        # for CORS to function properly.
        if('headers' not in response):
            response['headers'] = {
                'Access-Control-Allow-Origin': '*'
            }
        # Ship it!
        return response