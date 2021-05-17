import pytest
import requests
from time import time
from assertpy import assert_that
from .configuration import config
from api_test_utils.oauth_helper import OauthHelper
from api_test_utils.apigee_api_apps import ApigeeApiDeveloperApps
from api_test_utils.apigee_api_products import ApigeeApiProducts
from api_test_utils.apigee_api_trace import ApigeeApiTraceDebug


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
    def debug(self):
        """
        Import the test utils module to be able to:
            - Use the trace tool and get context variables after making a request to Apigee
        """
        return ApigeeApiTraceDebug(proxy='shared-flow-testing-internal-dev')

    @pytest.fixture()
    async def test_app_and_product(self, app, product):
        """Create a test app and product which can be modified in the test"""
        await product.create_new_product()

        await app.create_new_app()

        await product.update_scopes(
            [
                "urn:nhsd:apim:app:level3:shared-flow-testing",
                "urn:nhsd:apim:user-nhs-id:aal3:shared-flow-testing",
                "urn:nhsd:apim:user-nhs-login:P9:shared-flow-testing",
            ]
        )
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
            redirect_uri=test_app.callback_url,
        )
        token_resp = await oauth.get_token_response(grant_type="authorization_code")
        assert token_resp["status_code"] == 200
        return token_resp["body"]

    @pytest.fixture()
    async def get_token_client_credentials(self, test_app_and_product):
        """Call identity server to get an access token"""
        test_product, test_app = test_app_and_product
        oauth = OauthHelper(
            client_id=test_app.client_id,
            client_secret=test_app.client_secret,
            redirect_uri=test_app.callback_url,
        )
        jwt = oauth.create_jwt(kid="test-1")
        token_resp = await oauth.get_token_response(
            grant_type="client_credentials", _jwt=jwt
        )
        assert token_resp["status_code"] == 200
        return token_resp["body"]

    @pytest.fixture()
    async def get_token_nhs_login_token_exchange(self, test_app_and_product):
        """Call identity server to get an access token"""
        test_product, test_app = test_app_and_product
        oauth = OauthHelper(
            client_id=test_app.client_id,
            client_secret=test_app.client_secret,
            redirect_uri=test_app.callback_url,
        )

        id_token_claims = {
            "aud": "tf_-APIM-1",
            "id_status": "verified",
            "token_use": "id",
            "auth_time": 1616600683,
            "iss": "https://internal-dev.api.service.nhs.uk",
            "vot": "P9.Cp.Cd",
            "exp": int(time()) + 600,
            "iat": int(time()) - 10,
            "vtm": "https://auth.sandpit.signin.nhs.uk/trustmark/auth.sandpit.signin.nhs.uk",
            "jti": "b68ddb28-e440-443d-8725-dfe0da330118",
            "identity_proofing_level": "P9",
        }
        id_token_headers = {
            "sub": "49f470a1-cc52-49b7-beba-0f9cec937c46",
            "aud": "APIM-1",
            "kid": "nhs-login",
            "iss": "https://internal-dev.api.service.nhs.uk",
            "typ": "JWT",
            "exp": 1616604574,
            "iat": 1616600974,
            "alg": "RS512",
            "jti": "b68ddb28-e440-443d-8725-dfe0da330118",
        }
        with open(config.ID_TOKEN_NHS_LOGIN_PRIVATE_KEY_ABSOLUTE_PATH, "r") as f:
            contents = f.read()

        client_assertion_jwt = oauth.create_jwt(kid="test-1")
        id_token_jwt = oauth.create_id_token_jwt(
            algorithm="RS512",
            claims=id_token_claims,
            headers=id_token_headers,
            signing_key=contents,
        )

        # When
        token_resp = await oauth.get_token_response(
            grant_type="token_exchange",
            data={
                "grant_type": "urn:ietf:params:oauth:grant-type:token-exchange",
                "subject_token_type": "urn:ietf:params:oauth:token-type:id_token",
                "client_assertion_type": "urn:ietf:params:oauth:client-assertion-type:jwt-bearer",
                "subject_token": id_token_jwt,
                "client_assertion": client_assertion_jwt,
            },
        )
        assert token_resp["status_code"] == 200
        return token_resp["body"]

    @pytest.mark.asyncio
    async def test_happy_path(self, get_token):
        # Given
        token = get_token["access_token"]
        expected_status_code = 200

        # When
        response = requests.get(
            url="https://internal-dev.api.service.nhs.uk/shared-flow-testing/user-role-service",
            headers={
                "Authorization": f"Bearer {token}",
                "NHSD-Session-URID": "555254242102",
            },
        )

        # Then
        assert_that(expected_status_code).is_equal_to(response.status_code)

    @pytest.mark.asyncio
    async def test_default_role(self, get_token):
        # Given
        token = get_token["access_token"]
        expected_status_code = 200

        # When
        response = requests.get(
            url="https://internal-dev.api.service.nhs.uk/shared-flow-testing/user-role-service",
            headers={"Authorization": f"Bearer {token}"},
        )
        # Then
        assert_that(expected_status_code).is_equal_to(response.status_code)

    @pytest.mark.asyncio
    async def test_user_invalid_role_in_header(self, get_token, debug):
        # Given
        token = get_token["access_token"]
        expected_status_code = 400
        expected_error = "Bad Request"
        expected_error_description = "nhsd-session-urid is invalid"
        await debug.start_trace()

        # When
        response = requests.get(
            url="https://internal-dev.api.service.nhs.uk/shared-flow-testing/user-role-service",
            headers={
                "Authorization": f"Bearer {token}",
                "NHSD-Session-URID": "notAuserRole123",
            },
        )
        isSharedFlowError = await debug.get_apigee_variable_from_trace(name='sharedFlow.userRoleError')

        # Then
        assert_that(isSharedFlowError).is_equal_to('true')
        assert_that(expected_status_code).is_equal_to(response.status_code)
        assert_that(expected_error).is_equal_to(response.json()["issue"][0]["details"]["coding"][0]["display"])
        assert_that(expected_error_description).is_equal_to(response.json()["issue"][0]["diagnostics"])

    @pytest.mark.asyncio
    async def test_no_role_provided(self, get_token_client_credentials, debug):
        token = get_token_client_credentials["access_token"]
        # Given
        expected_status_code = 400
        expected_error = "Bad Request"
        expected_error_description = "selected_roleid is missing in your token"
        await debug.start_trace()

        # When
        response = requests.get(
            url="https://internal-dev.api.service.nhs.uk/shared-flow-testing/user-role-service",
            headers={"Authorization": f"Bearer {token}"},
        )
        isSharedFlowError = await debug.get_apigee_variable_from_trace(name='sharedFlow.userRoleError')
        # Then
        assert_that(isSharedFlowError).is_equal_to('true')
        assert_that(expected_status_code).is_equal_to(response.status_code)
        assert_that(expected_error).is_equal_to(response.json()["issue"][0]["details"]["coding"][0]["display"])
        assert_that(expected_error_description).is_equal_to(response.json()["issue"][0]["diagnostics"])

    @pytest.mark.asyncio
    async def test_nhs_login_exchanged_token_no_role_provided(
        self, get_token_nhs_login_token_exchange, debug
    ):
        token = get_token_nhs_login_token_exchange["access_token"]
        # Given
        expected_status_code = 400
        expected_error = "Bad Request"
        expected_error_description = "selected_roleid is missing in your token"
        await debug.start_trace()

        # When
        response = requests.get(
            url="https://internal-dev.api.service.nhs.uk/shared-flow-testing/user-role-service",
            headers={"Authorization": f"Bearer {token}"},
        )
        isSharedFlowError = await debug.get_apigee_variable_from_trace(name='sharedFlow.userRoleError')
        # Then
        assert_that(isSharedFlowError).is_equal_to('true')
        assert_that(expected_status_code).is_equal_to(response.status_code)
        assert_that(expected_error).is_equal_to(response.json()["issue"][0]["details"]["coding"][0]["display"])
        assert_that(expected_error_description).is_equal_to(response.json()["issue"][0]["diagnostics"])

    @pytest.mark.asyncio
    async def test_no_role_id_on_id_token(self, test_app_and_product):
        """Call identity server to get an access token"""
        # Given
        expected_status_code = 400

        test_product, test_app = test_app_and_product
        oauth = OauthHelper(
            client_id=test_app.client_id,
            client_secret=test_app.client_secret,
            redirect_uri=test_app.callback_url,
        )
        jwt = oauth.create_jwt(kid="test-1")
        token_resp = await oauth.get_token_response(
            grant_type="client_credentials", _jwt=jwt
        )
        # When
        response = requests.get(
            url="https://internal-dev.api.service.nhs.uk/shared-flow-testing/user-role-service",
            headers={
                "Authorization": f"Bearer {token_resp['body']['access_token']}",
                "NHSD-Session-URID": "123456789",
            },
        )
        # Then
        assert_that(expected_status_code).is_equal_to(response.status_code)
