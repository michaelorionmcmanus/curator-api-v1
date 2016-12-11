import os, json
here = os.path.dirname(os.path.realpath(__file__))
from conftest import playback, record, expected_response_body

def test_patch_method(app, dynamo_db_session, event):
    playback(__file__, dynamo_db_session)
    context = {}
    event['httpMethod'] = 'PATCH'
    event['body'] = json.dumps([
        {
            'op': 'add',
            'path': '/cognito-identities/1',
            'value': 'us-west-2:a47a4d81-7043-42ec-8956-dd4e39c3b51a'
        }
    ])
    actual_response = app.users_controller(event, context)
    assert actual_response['statusCode'] == 204