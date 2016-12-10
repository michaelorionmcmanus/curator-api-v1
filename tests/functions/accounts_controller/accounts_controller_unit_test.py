def test_no_boom():
    module = __import__('app.functions.accounts_controller.handler')
    assert module