import os, json
here = os.path.dirname(os.path.realpath(__file__))
from conftest import playback, record, expected_response_body

def test_get_method(app, dynamo_db_session, event):
    playback(__file__, dynamo_db_session)
    context = {}
    actual_response = app.accounts_controller(event, context)
    actual_response_body = json.loads(actual_response['body'])
    assert actual_response['statusCode'] == 200, 'The response statusCode is 200'
    assert actual_response_body == expected_response_body(here, 'expectations/test_get_method.yml', actual_response), 'Expected response body matches the actual response body.'

def test_post_method(app, dynamo_db_session, event):
    playback(__file__, dynamo_db_session)
    context = {}
    event['httpMethod'] = 'POST'
    event['body'] = '{"data":{"attributes":{"name":"Test","members":[],"owners":[],"is-owner":false},"type":"accounts"}}'
    actual_response = app.accounts_controller(event, context)
    actual_response_body = json.loads(actual_response['body'])
    assert actual_response['statusCode'] == 201, 'The response statusCode is 201'
    assert actual_response_body == expected_response_body(here, 'expectations/test_post_method.yml', actual_response), 'Expected response body matches the actual response body.'