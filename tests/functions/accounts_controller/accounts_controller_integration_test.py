import pytest, imp, yaml, sys, os, json, yaml
here = os.path.dirname(os.path.realpath(__file__))
import placebo
from botocore import session as boto_session
session = boto_session.get_session()
session.events = session.get_component('event_emitter')
pill = placebo.attach(session, data_path=os.path.join(here, 'placebos'))
pill.playback()
run = __import__('run')

def test_get_method():
    with open('base-event.yml') as data_file:
        event = yaml.load(data_file)
    context = {}
    actual_response = run.accounts_controller(event, context, session)
    actual_response_body = json.loads(actual_response['body'])
    expected_response_body = yaml.load(open(here + '/expectations/test_get_method.yml'))
    assert actual_response['statusCode'] == 200, 'The response statusCode is 200'
    assert actual_response_body == expected_response_body, 'Expected response body matches the actual response body.'