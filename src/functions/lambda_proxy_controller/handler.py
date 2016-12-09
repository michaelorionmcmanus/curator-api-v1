from orion.providers.aws.clients import dynamo_db
import orion.providers.aws.controllers.lambda_proxy_event as lambda_proxy
# Establish connection on container startup.
dynamo_db.connect()

@lambda_proxy.get
def get_method(event, context, **kwargs):
    return 'GET'

@lambda_proxy.post
def post_handler(event, context, **kwargs):
    return 'POST'