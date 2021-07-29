import pytest
import requests
from api_test_utils.oauth_helper import OauthHelper
from assertpy import assert_that

from .configuration import config


class TestEndpoints:
    @pytest.mark.asyncio
    async def test_happy_path(self, get_token):
        # Given
        token = get_token["access_token"]
        expected_status_code = 200

        # When
        response = requests.get(
            url=f"https://internal-dev.api.service.nhs.uk/{config.SERVICE_BASE_PATH}/user-role-service",
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
            url=f"https://internal-dev.api.service.nhs.uk/{config.SERVICE_BASE_PATH}/user-role-service",
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
            url=f"https://internal-dev.api.service.nhs.uk/{config.SERVICE_BASE_PATH}/user-role-service",
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
            url=f"https://internal-dev.api.service.nhs.uk/{config.SERVICE_BASE_PATH}/user-role-service",
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
            url=f"https://internal-dev.api.service.nhs.uk/{config.SERVICE_BASE_PATH}/user-role-service",
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
            url=f"https://internal-dev.api.service.nhs.uk/{config.SERVICE_BASE_PATH}/user-role-service",
            headers={
                "Authorization": f"Bearer {token_resp['body']['access_token']}",
                "NHSD-Session-URID": "123456789",
            },
        )
        # Then
        assert_that(expected_status_code).is_equal_to(response.status_code)
