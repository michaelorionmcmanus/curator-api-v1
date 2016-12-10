def test_no_boom():
    module = __import__('src.functions.accounts_controller.handler')
    assert module