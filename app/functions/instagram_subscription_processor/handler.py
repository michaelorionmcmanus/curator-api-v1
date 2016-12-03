from slsrequest import BaseRequest
import json, requests, arrow, uuid, re, os, boto3

class InstagramSubscriptionProcessor(BaseRequest):
    def __init__(self, event, context):
        BaseRequest.__init__(self, event, context)
        self.log('Initialized InstagramSubscriptionProcessor instance') 
        
    def get_handler(self, event, context, principal_id):
        self.log(json.dumps(event))
        if(event['queryStringParameters']['hub_mode'] == 'subscribe'):
            self.log('Responding to challenge. Allowing subscription for ' + event['queryStringParameters']['hub_verify_token'])
            return { 'passthrough': event['queryStringParameters']['hub_challenge'] }

    def post_handler(self, event, context, principal_id):
        self.log(json.dumps(event))

def handler(event, context):
    SlsRequestInstance = InstagramSubscriptionProcessor(event, context)
    return SlsRequestInstance.handler(event=event, context=context)