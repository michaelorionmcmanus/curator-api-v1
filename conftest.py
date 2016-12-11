# content of conftest.py
import pytest, os, sys, importlib, yaml, json
here = os.path.dirname(os.path.realpath(__file__))
sys.path = [os.path.join(here, "app/tight")] + sys.path

from botocore import session as boto_session
from tight.providers.aws.clients import dynamo_db
import placebo

def pytest_sessionstart():
    os.environ['STAGE'] = 'dev'
    os.environ['SERVERLESS_REGION'] = 'us-west-2'
    os.environ['SERVERLESS_SERVICE_NAME'] = 'curator-api-v1'
    if 'CI' not in os.environ:
        os.environ['CI'] = 'False'
        os.environ['USE_LOCAL_DB'] = 'True'

@pytest.fixture
def app():
    return importlib.import_module('app_index')

@pytest.fixture
def event():
    with open('base-event.yml') as data_file:
        event = yaml.load(data_file)
    return event

def spy_on_dynamo_db(file, dynamo_db_session):
    test_path = '/'.join(file.split('/')[0:-1])
    pills_path = '/'.join([test_path, 'placebos'])
    pill = placebo.attach(dynamo_db_session, data_path=pills_path)
    return pill

def record(file, dynamo_db_session):
    pill = spy_on_dynamo_db(file, dynamo_db_session)
    os.environ['RECORD'] = 'True'
    pill.record()
    return pill

def playback(file, dynamo_db_session):
    pill = spy_on_dynamo_db(file, dynamo_db_session)
    os.environ['PLAYBACK'] = 'True'
    pill.playback()
    return pill

def expected_response_body(dir, expectation_file, actual_response):
    file_path = '/'.join([dir, expectation_file])
    if 'PLAYBACK' in os.environ and os.environ['PLAYBACK'] == 'True':
        return json.loads(yaml.load(open(file_path))['body'])
    if 'RECORD' in os.environ and os.environ['RECORD'] == 'True':
        stream = file(file_path, 'w')
        yaml.safe_dump(actual_response, stream)
        return json.loads(actual_response['body'])


@pytest.fixture
def dynamo_db_session():
    session =  getattr(dynamo_db, 'session') or None
    if session:
        return session
    else:
        session = boto_session.get_session()
        session.events = session.get_component('event_emitter')
        dynamo_db.session = session
        return session