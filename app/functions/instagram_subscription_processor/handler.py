from slsrequest import BaseRequest
import json, requests, arrow, uuid, re, os
import tight.providers.aws.controllers.lambda_proxy_event as lambda_proxy
from tight.core.logger import info
from tight.core.safeget import safeget

@lambda_proxy.get
def get_handler(*args, **kwargs):
    event = kwargs.pop('event')
    info(message=json.dumps(event))
    hub_mode = safeget(event, 'queryStringParameters', 'hub_mode')
    hub_verify_token = safeget(event, 'queryStringParameters', 'hub_verify_token')
    hub_challenge = safeget(event, 'queryStringParameters', 'hub_challenge')
    if(hub_mode == 'subscribe'):
        info(message='Responding to challenge. Allowing subscription for {}'.format(hub_verify_token))
        return { 'passthrough': hub_challenge }

@lambda_proxy.post
def post_handler(*args, **kwargs):
    event = kwargs.pop('event')
    info(message=json.dumps(event))