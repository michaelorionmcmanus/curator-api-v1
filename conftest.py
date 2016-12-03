# content of conftest.py
import pytest, os

@pytest.fixture(scope="session", autouse=True)
def default_env():
    os.environ['STAGE'] = 'dev'
    os.environ['SERVERLESS_REGION'] = 'us-west-2'
    os.environ['SERVERLESS_SERVICE_NAME'] = 'curator-api-v1'
    # CI is indicated by global environment. We default to off for local dev. 
    if 'CI' not in os.environ:
        os.environ['CI'] = 'False'