from orion.providers.aws.clients import dynamo_db
import orion.providers.aws.controllers.lambda_proxy_event as lambda_proxy
dynamo_db.connect()

@lambda_proxy.get
def get_method(*args, **kwargs):
    return {
        'body': 'GET'
    }

@lambda_proxy.post
def post_handler(*args, **kwargs):
    return {
        'body': 'POST'
    }