import yaml

def test_get_method():
    handler = __import__('src.functions.lambda_proxy_controller.handler', fromlist=['handler'])
    with open('base-event.yml') as data_file:
        event = yaml.load(data_file)
    context = {}
    actual_response = handler.handler(event, context)
    assert actual_response == 'GET'

def test_post_method():
    run = __import__('app')
    with open('base-event.yml') as data_file:
        event = yaml.load(data_file)
    event['httpMethod'] = 'POST'
    context = {}
    actual_response = run.lambda_proxy_controller(event, context)
    assert actual_response == 'POST'