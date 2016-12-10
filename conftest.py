# content of conftest.py
import pytest, os, sys, importlib, yaml
here = os.path.dirname(os.path.realpath(__file__))
sys.path = [os.path.join(here, "app/tight")] + sys.path

from botocore import session as boto_session
from tight.providers.aws.clients import dynamo_db
import placebo

@pytest.fixture(scope="session", autouse=True)
def default_env():
    os.environ['STAGE'] = 'dev'
    os.environ['SERVERLESS_REGION'] = 'us-west-2'
    os.environ['SERVERLESS_SERVICE_NAME'] = 'curator-api-v1'
    if 'CI' not in os.environ:
        os.environ['CI'] = 'False'

@pytest.fixture
def app():
    return importlib.import_module('app_index')

@pytest.fixture
def event():
    with open('base-event.yml') as data_file:
        event = yaml.load(data_file)
    return event


def spy_on_dynamo_db(func):
    test_path = '/'.join(func.func_globals['__file__'].split('/')[0:-1])
    pills_path = '/'.join([test_path, 'placebos'])
    pill = placebo.attach(dynamo_db.session, data_path=pills_path)
    return pill

def placebo_record(func):
    pill = spy_on_dynamo_db(func)
    pill.record()
    return func

def placebo_playback(func):
    pill = spy_on_dynamo_db(func)
    pill.playback()
    return func

def dynamo_db_init(func):
    if 'CI' not in os.environ:
        os.environ['USE_LOCAL_DB'] = 'True'
    session = boto_session.get_session()
    session.events = session.get_component('event_emitter')
    dynamo_db.session = session
    return func