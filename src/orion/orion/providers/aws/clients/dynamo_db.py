from flywheel import Model, Field, Engine
import os

session = None

def connect(*args, **kwargs):
    engine = Engine()
    # Connect the engine to either a local DynamoDB or a particular region.
    if ('USE_LOCAL_DB' in os.environ and os.environ['USE_LOCAL_DB'] == 'True'):
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