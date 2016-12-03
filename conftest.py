# content of conftest.py
import pytest, os

@pytest.fixture(scope="session", autouse=True)
def default_ci_env():
    # CI is indicated by global environment. We default to off for local dev. 
    if 'CI' not in os.environ:
        os.environ['CI'] = 'False'