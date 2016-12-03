import pytest

def test_no_boom():
    module = __import__('app.functions.accounts_controller.handler', fromlist=['AccountsController'])
    AccountsController = module.AccountsController
    event = {}
    context = {}
    controller_instance = AccountsController(event, context)
    assert controller_instance