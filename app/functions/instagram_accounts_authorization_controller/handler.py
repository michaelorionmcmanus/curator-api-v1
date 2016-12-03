from slsrequest import BaseRequest
import json, requests, arrow, uuid, re, os, boto3
from apiclients import InstagramClient

class InstagramAccountsAuthorizationController(BaseRequest):
    def __init__(self, event, context):
        BaseRequest.__init__(self, event, context)
        self.instagram_client = InstagramClient()
        self.log('Initialized InstagramAccountsAuthorizationController instance') 
        
    def get_handler(self, event, context, principal_id):
        self.instagram_client.set_redirect_uri(event['queryStringParameters']['redirect_uri'])
        return {
            'body': {
                'data': {
                    'type': 'instagram-authorization',
                    'id': 1,
                    'attributes': {
                        'url': self.instagram_client.get_unauthenticated_api().get_authorize_url(scope=["likes", "comments", "public_content"])
                    }
                }
            }
        }

def handler(event, context):
    SlsRequestInstance = InstagramAccountsAuthorizationController(event, context)
    return SlsRequestInstance.handler(event=event, context=context)