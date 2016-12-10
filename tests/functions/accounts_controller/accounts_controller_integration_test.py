import os, json, yaml, importlib
here = os.path.dirname(os.path.realpath(__file__))
from conftest import playback

def test_get_method(dynamo_db_session, event):
    module = __import__('app_index')
    playback(__file__, dynamo_db_session)
    context = {}
    actual_response = module.accounts_controller(event, context)
    actual_response_body = json.loads(actual_response['body'])
    expected_response_body = yaml.load(open(here + '/expectations/test_get_method.yml'))
    assert actual_response['statusCode'] == 200, 'The response statusCode is 200'
    assert actual_response_body == expected_response_body, 'Expected response body matches the actual response body.'