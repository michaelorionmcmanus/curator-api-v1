from __future__ import print_function
import os
from instagram import client, subscriptions

class InstagramClient(object):
    def __init__(self):
        INSTAGRAM_CLIENT_ID = os.environ.get('INSTAGRAM_CLIENT_ID')
        INSTAGRAM_CLIENT_SECRET = os.environ.get('INSTAGRAM_CLIENT_SECRET')
        INSTAGRAM_API_CONFIG = {
            'client_id': INSTAGRAM_CLIENT_ID,
            'client_secret': INSTAGRAM_CLIENT_SECRET,
            'redirect_uri': 'http://localhost:4200/settings/instagram-accounts'
        }
        self.CONFIG = INSTAGRAM_API_CONFIG

    def log(self, message):
        log.info(message)

    def get_unauthenticated_api(self):
        return client.InstagramAPI(**self.CONFIG)

    def get_authenticated_api(self, access_token):
        return client.InstagramAPI(access_token=access_token, client_secret=self.CONFIG['client_secret'])

    def get_user(self, access_token):
        api = self.get_authenticated_api(access_token=access_token)
        return api.user()

    def set_redirect_uri(self, uri):
        self.CONFIG['redirect_uri'] = uri