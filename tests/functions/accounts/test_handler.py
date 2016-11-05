import pytest
from app.functions.accounts_controller.handler import AccountsController
from util.load_env import load


@pytest.fixture(autouse=True)
def no_requests(monkeypatch):
    monkeypatch.delattr("requests.sessions.Session.request")

def setup_module(module):
    load(aws_profile="serverless-admin")

def test_no_boom():
    event = {}
    context = {}
    controller_instance = AccountsController(event, context)
    assert controller_instance