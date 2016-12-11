import pytest, os, sys, importlib, yaml, json
from botocore import session as boto_session
from tight.providers.aws.clients import boto3_client
from tight.providers.aws.clients import dynamo_db
import placebo

@pytest.fixture
def app():
    return importlib.import_module('app_index')

@pytest.fixture
def event():
    with open('base-event.yml') as data_file:
        event = yaml.load(data_file)
    return event

def placebos_path(file):
    test_path = '/'.join(file.split('/')[0:-1])
    path = '/'.join([test_path, 'placebos'])
    return path

def spy_on_session(file, session):
    pill = placebo.attach(session, data_path=placebos_path(file))
    return pill

def record(file, dynamo_db_session):
    this = sys.modules[__name__]
    if not hasattr(this, 'pill') or not hasattr(this, 'boto3_pill'):
        boto3_session = boto3_client.session()
        boto3_pill = spy_on_session(file, boto3_session)
        boto3_pill.record()
        pill = spy_on_session(file, dynamo_db_session)
        os.environ['RECORD'] = 'True'
        pill.record()
        setattr(this, 'pill', pill)
        setattr(this, 'boto3_pill', boto3_pill)

def playback(file, dynamo_db_session):
    this = sys.modules[__name__]
    if not hasattr(this, 'pill') or not hasattr(this, 'boto3_pill'):
        boto3_session = boto3_client.session()
        boto3_pill = spy_on_session(file, boto3_session)
        boto3_pill.playback()
        pill = spy_on_session(file, dynamo_db_session)
        os.environ['PLAYBACK'] = 'True'
        pill.playback()
        setattr(this, 'pill', pill)
        setattr(this, 'boto3_pill', boto3_pill)
    else:
        getattr(this, 'pill')._data_path = placebos_path(file)
        getattr(this, 'boto3_pill')._data_path = placebos_path(file)

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