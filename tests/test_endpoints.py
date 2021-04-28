import pytest
import requests
from assertpy import assert_that
from api_test_utils.oauth_helper import OauthHelper
from api_test_utils.apigee_api_apps import ApigeeApiDeveloperApps
from api_test_utils.apigee_api_products import ApigeeApiProducts


class TestEndpoints:

    @pytest.fixture()
    def app(self):
        """
        Import the test utils module to be able to:
            - Create apigee test application
                - Update custom attributes
                - Update custom ratelimits
                - Update products to the test application
        """
        return ApigeeApiDeveloperApps()

    @pytest.fixture()
    def product(self):
        """
        Import the test utils module to be able to:
            - Create apigee test product
                - Update custom scopes
                - Update environments
                - Update product paths
                - Update custom attributes
                - Update proxies to the product
                - Update custom ratelimits
        """
        return ApigeeApiProducts()

    @pytest.fixture()
    async def test_app_and_product(self, app, product):
        """Create a test app and product which can be modified in the test"""
        await product.create_new_product()

        await app.create_new_app()

        await product.update_scopes([
            "urn:nhsd:apim:app:level3:shared-flow-testing",
            "urn:nhsd:apim:user-nhs-id:aal3:shared-flow-testing"
        ])
        await app.add_api_product([product.name])
        await app.set_custom_attributes(
            {
                "jwks-resource-url": "https://raw.githubusercontent.com/NHSDigital/"
                "identity-service-jwks/main/jwks/internal-dev/"
                "9baed6f4-1361-4a8e-8531-1f8426e3aba8.json"
            }
        )

        yield product, app

        await app.destroy_app()
        await product.destroy_product()

    @pytest.fixture()
    async def get_token(self, test_app_and_product):
        """Call identity server to get an access token"""
        test_product, test_app = test_app_and_product
        oauth = OauthHelper(
            client_id=test_app.client_id,
            client_secret=test_app.client_secret,
            redirect_uri=test_app.callback_url
            )
        token_resp = await oauth.get_token_response(grant_type="authorization_code")
        assert token_resp["status_code"] == 200
        return token_resp['body']

    @pytest.fixture()
    async def get_token_client_credentials(self, test_app_and_product):
        """Call identity server to get an access token"""
        test_product, test_app = test_app_and_product
        oauth = OauthHelper(
            client_id=test_app.client_id,
            client_secret=test_app.client_secret,
            redirect_uri=test_app.callback_url
            )
        jwt = oauth.create_jwt(kid="test-1")
        token_resp = await oauth.get_token_response(
            grant_type="client_credentials", _jwt=jwt
        )
        assert token_resp["status_code"] == 200
        return token_resp['body']

    def test_user_invalid_role_in_header(self, get_token):
        # Given
        token = get_token['access_token']
        expected_status_code = 400
        expected_error = "invalid role"
        expected_error_description = "nhsd-session-urid is invalid"

        # When
        response = requests.get(
            url='https://internal-dev.api.service.nhs.uk/shared-flow-testing/user-role-service',
            headers={
                "Authorization": f"Bearer {token}",
                "NHSD-Session-URID": "notAuserRole123",
            },
        )

        # Then
        assert_that(expected_status_code).is_equal_to(response.status_code)
        assert_that(expected_error).is_equal_to(response.json()["error"])
        assert_that(expected_error_description).is_equal_to(
            response.json()["error_description"]
        )

    # def test_no_role_provided(self, get_token_client_credentials):
    #     token = get_token_client_credentials['access_token']
    #     # Given
    #     expected_status_code = 400
    #     expected_error = "invalid role"
    #     expected_error_description = "selected_roleid is missing in your token"

    #     # When
    #     response = requests.get(
    #         url='https://internal-dev.api.service.nhs.uk/shared-flow-testing/user-role-service',
    #         headers={"Authorization": f"Bearer {token}"},
    #     )
    #     # Then
    #     assert_that(expected_status_code).is_equal_to(response.status_code)
    #     assert_that(expected_error).is_equal_to(response.json()["error"])
    #     assert_that(expected_error_description).is_equal_to(
    #         response.json()["error_description"]
    #     )
