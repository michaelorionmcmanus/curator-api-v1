from orion.providers.aws.controllers.lambda_proxy_event import (
    get, post, handler as lambda_proxy
)

@get
def get_method(event, context, **kwargs):
    return 'GET'

@post
def post_handler(event, context, **kwargs):
    return 'POST'

def handler(*args, **kwargs):
    return lambda_proxy(*args, **kwargs)