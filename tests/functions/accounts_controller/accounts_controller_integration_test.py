import os, json, yaml
here = os.path.dirname(os.path.realpath(__file__))
import placebo
from botocore import session as boto_session
session = boto_session.get_session()
session.events = session.get_component('event_emitter')
pill = placebo.attach(session, data_path=os.path.join(here, 'placebos'))
pill.playback()

def test_get_method():
    # We want to be able to access local db when building placebos
    os.environ['USE_LOCAL_DB'] = 'True'
    # Import our module.
    run = __import__('run')
    # Get a base lambda proxy event
    with open('base-event.yml') as data_file:
        event = yaml.load(data_file)
    # Build some context 
    context = {}
    # Run the controller
    actual_response = run.accounts_controller(event, context, session)
    actual_response_body = json.loads(actual_response['body'])
    expected_response_body = yaml.load(open(here + '/expectations/test_get_method.yml'))
    assert actual_response['statusCode'] == 200, 'The response statusCode is 200'
    assert actual_response_body == expected_response_body, 'Expected response body matches the actual response body.'