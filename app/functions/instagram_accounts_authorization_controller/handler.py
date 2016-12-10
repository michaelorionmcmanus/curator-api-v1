from apiclients import InstagramClient
import tight.providers.aws.controllers.lambda_proxy_event as lambda_proxy
instagram_client = InstagramClient()

@lambda_proxy.get
def get_handler(*args, **kwargs):
    event = kwargs.pop('event')
    instagram_client.set_redirect_uri(event['queryStringParameters']['redirect_uri'])
    return {
        'body': {
            'data': {
                'type': 'instagram-authorization',
                'id': 1,
                'attributes': {
                    'url': instagram_client.get_unauthenticated_api().get_authorize_url(scope=["likes", "comments", "public_content"])
                }
            }
        }
    }