import os, json, yaml
here = os.path.dirname(os.path.realpath(__file__))
from conftest import dynamo_db_init
from tight.providers.aws.clients import dynamo_db

@dynamo_db_init
def test_get_method(app, event):
    context = {}
    # Run the controller
    event['queryStringParameters'] = {
        'redirect_uri': 'https://www.banana.com'
    }
    actual_response = app.instagram_accounts_authorization_controller(event, context, session=dynamo_db.session)
    json.loads(actual_response['body'])
    assert True, 'no boom'