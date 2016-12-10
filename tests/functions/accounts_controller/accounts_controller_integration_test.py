import os, json, yaml
here = os.path.dirname(os.path.realpath(__file__))
from conftest import dynamo_db_init, placebo_playback
from tight.providers.aws.clients import dynamo_db

@placebo_playback
@dynamo_db_init
def test_get_method(app, event):
    context = {}
    # Run the controller
    actual_response = app.accounts_controller(event, context, session=dynamo_db.session)
    actual_response_body = json.loads(actual_response['body'])
    expected_response_body = yaml.load(open(here + '/expectations/test_get_method.yml'))
    assert actual_response['statusCode'] == 200, 'The response statusCode is 200'
    assert actual_response_body == expected_response_body, 'Expected response body matches the actual response body.'