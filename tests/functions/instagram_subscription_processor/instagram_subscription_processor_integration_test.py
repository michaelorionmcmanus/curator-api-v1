def test_get_method(app, dynamo_db_session, event):
    context = {}
    event['queryStringParameters'] = {
        'hub_mode': 'subscribe',
        'hub_verify_token': 'hub_verify_token',
        'hub_challenge': 'hub_challenge'
    }
    actual_response = app.instagram_subscription_processor(event, context)
    assert actual_response == 'hub_challenge'

def test_post_method(app, dynamo_db_session, event):
    context = {}
    app.accounts_controller(event, context)
    assert True, 'No boom boom'
