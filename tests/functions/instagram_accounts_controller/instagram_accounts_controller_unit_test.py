import pytest, responses, importlib

@responses.activate
def test_get_instagram_account_credentials_success():
    module = importlib.import_module('app.functions.instagram_accounts_controller.handler')
    code = 'some_code'
    redirect_uri = 'http://localhost:4200/accounts/dashboard/instagram-accounts?account_id=656b0bb4-3c02-41c1-8aa3-6761973e1b91'
    expected_access_token = '2003123.538a604.85334889cbf946e289ffa647034c63d9'
    expected_account_info = {"username": "codermichael", "bio": "", "website": "", "profile_picture": "https://scontent.cdninstagram.com/t51.2885-19/11348122_569648069839553_1836103301_a.jpg", "full_name": "MM", "id": "2003123"}
    responses.add(responses.POST, 'https://api.instagram.com/oauth/access_token',
                json={"access_token": expected_access_token, "user": expected_account_info},
                status=200,
                content_type='application/json'
                )
    actual_credentials = module.get_instagram_account_credentials(code, redirect_uri)
    assert actual_credentials['access_token'] == expected_access_token
    assert actual_credentials['account_info'] == expected_account_info

@responses.activate
def test_get_instagram_account_credentials_code_used():
    module = importlib.import_module('app.functions.instagram_accounts_controller.handler')
    code = 'some_code'
    redirect_uri = 'http://localhost:4200/accounts/dashboard/instagram-accounts?account_id=656b0bb4-3c02-41c1-8aa3-6761973e1b91'
    responses.add(responses.POST, 'https://api.instagram.com/oauth/access_token',
                json={"code": 400, "error_type": "OAuthException", "error_message": "Matching code was not found or was already used."},
                status=400,
                content_type='application/json'
                )

    expected_exception_message = {'body': {'errors': [{'message': u'Matching code was not found or was already used.', 'data': {'error_type': u'OAuthException'}}]}, 'statusCode': 400}
    with pytest.raises(Exception) as excinfo:
        try:
            actual_response = module.get_instagram_account_credentials(code, redirect_uri)
        except Exception as e:
            assert expected_exception_message == e.message
            raise Exception(e)
