def test_get_method(app, event):
    context = {}
    actual_response = app.lambda_proxy_controller(event, context)
    assert actual_response['body'] == 'GET'

def test_post_method(app, event):
    event['httpMethod'] = 'POST'
    context = {}
    actual_response = app.lambda_proxy_controller(event, context)
    assert actual_response['body'] == 'POST'