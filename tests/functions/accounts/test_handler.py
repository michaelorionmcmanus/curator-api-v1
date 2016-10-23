import os, sys
here = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.join(here, "../../../app/functions/accounts-manager"))
sys.path.append(os.path.join(here, "../../../app/shared"))
sys.path.append(os.path.join(here, "../../../app/vendored"))
import pytest
from handler import AccountsManager
from util.load_env import load


@pytest.fixture(autouse=True)
def no_requests(monkeypatch):
    monkeypatch.delattr("requests.sessions.Session.request")

def setup_module(module):
    load(aws_profile="serverless-admin")

def test_no_boom():
    manager_instance = AccountsManager()
    assert manager_instance