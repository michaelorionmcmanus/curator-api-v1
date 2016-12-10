import yaml
from conftest import dynamo_db_init, placebo_playback

def test_get_method():
    app = __import__('app')
    with open('base-event.yml') as data_file:
        event = yaml.load(data_file)
    context = {}
    actual_response = app.lambda_proxy_controller(event, context)
    assert actual_response['body'] == 'GET'

def test_post_method():
    app = __import__('app')
    with open('base-event.yml') as data_file:
        event = yaml.load(data_file)
    event['httpMethod'] = 'POST'
    context = {}
    actual_response = app.lambda_proxy_controller(event, context)
    assert actual_response['body'] == 'POST'