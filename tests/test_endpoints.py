import pytest
import requests

from .configuration import config


class TestEndpoints:
    """ A test suite for testing endpoints"""
    async def get_access_token(self, test_app, user_id, webdriver_session):

        code = await test_app.oauth.get_authenticated_with_mock_auth(user_id, webdriver_session)

        token_resp = await test_app.oauth.hit_oauth_endpoint(
            method="POST",
            endpoint="token",
            data={
                'client_id': test_app.oauth.client_id,
                'client_secret': test_app.oauth.client_secret,
                'grant_type': "authorization_code",
                'redirect_uri': test_app.oauth.redirect_uri,
                'code': code
            }
        )

        return token_resp["body"]["access_token"]

    async def call_user_info(self, test_app, access_token):
        user_info_resp = await test_app.oauth.hit_oauth_endpoint(
            method="GET",
            endpoint="userinfo",
            headers={"Authorization": f"Bearer {access_token}"}
        )

        return user_info_resp

    @pytest.mark.asyncio
    async def test_mock_auth(self, test_app_and_product, webdriver_session):
        test_product, test_app = test_app_and_product
        user_id = "656005750107"
        access_token = await self.get_access_token(test_app, user_id, webdriver_session)

        userinfo_resp = await self.call_user_info(test_app, access_token)

        assert userinfo_resp['status_code'] == 200

    @pytest.mark.asyncio
    @pytest.mark.parametrize("user_id,status_code,additional_headers", [
        (
            "656005750107",  # User role sent in id token
            200,
            {}
        ),
        (
            "787807429512",  # User role in user info (no header, not in id token),
            200,
            {}
        ),
        (
            "Aal3",  # User role sent in header
            200,
            {"NHSD-Session-URID": "555254242102"}
        )
    ])
    async def test_user_role_happy_path(self, test_app_and_product, webdriver_session,
                                        user_id, status_code, additional_headers):
        test_product, test_app = test_app_and_product
        access_token = await self.get_access_token(test_app, user_id, webdriver_session)
        headers = {
                "Authorization": f"Bearer {access_token}",
        }
        for key, value in additional_headers.items():
            headers[key] = value

        response = requests.get(
            url=f"https://internal-dev.api.service.nhs.uk/{config.SERVICE_BASE_PATH}/user-role-service",
            headers=headers
        )

        assert response.status_code == status_code

    @pytest.mark.asyncio
    @pytest.mark.parametrize("user_id,status_code,additional_headers,error_description", [
        (
            "656005750104",  # Multiple user roles found in userinfo
            400,
            {},
            "multiple roles found in user info"
        ),
        (
            "Aal3",  # No user role provided by any means
            400,
            {},
            "no userroles available, please check nhsd-session-urid is valid"
        ),
        (
            "Aal4",  # User role sent in id token but empty
            400,
            {},
            "selected_roleid is misconfigured/invalid"
        ),
        (
            "Aal5",  # nrbac is malformed, or person_roleid is empty (in userinfo)
            400,
            {},
            "nhsid_nrbac_roles is misconfigured/invalid"
        ),
        (
            # TODO not sure if this will work, sending an invalid user? will try and run a manual test
            "notAValidUser",  # Unable to get user info for this user
            400,
            {},
            "unable to retrieve user info"
        ),
        (
            # TODO - This must be implemented in the flow logic as error + then have the error descp filled in below
            "Aal3",  # Invalid role in header
            400,
            {"NHSD-Session-URID": "notAuserRole123"},
            ""
        )
    ])
    async def test_user_role_unhappy_path(self, test_app_and_product, webdriver_session,
                                          debug, user_id, status_code, additional_headers, error_description):
        test_product, test_app = test_app_and_product
        access_token = await self.get_access_token(test_app, user_id, webdriver_session)
        headers = {
                "Authorization": f"Bearer {access_token}",
        }
        for key, value in additional_headers.items():
            headers[key] = value

        await debug.start_trace()

        response = requests.get(
            url=f"https://internal-dev.api.service.nhs.uk/{config.SERVICE_BASE_PATH}/user-role-service",
            headers=headers
        )

        isSharedFlowError = await debug.get_apigee_variable_from_trace(name='sharedFlow.userRoleError')
        assert isSharedFlowError == 'true'
        assert response.status_code == status_code
        assert response.json()["issue"][0]["diagnostics"] == error_description
