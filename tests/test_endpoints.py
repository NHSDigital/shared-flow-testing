# import pytest
# import requests

# from .utils import config


# class TestEndpoints:
#     """ A test suite for testing endpoints"""
#     async def get_access_token(self, test_app, user_id):

#         token_resp = test_app.oauth.get_authenticated_with_mock_auth(user_id)

#         return token_resp["access_token"]

#     @pytest.mark.mock_auth
#     @pytest.mark.asyncio
#     @pytest.mark.parametrize("user_id,status_code,additional_headers", [
#         (
#             "656005750107",  # User role sent in id token
#             200,
#             {}
#         ),
#         (
#             "787807429512",  # User role in user info - one role - (no header, not in id token),
#             200,
#             {}
#         ),
#         (
#             "656005750104",  # User role sent in header (no in id token, multiple in user info)
#             200,
#             {"NHSD-Session-URID": "656014452101"}
#         )
#     ])
#     async def test_user_role_happy_path(self, test_app_and_product,
#                                         user_id, status_code, additional_headers):
#         test_product, test_app = test_app_and_product
#         access_token = await self.get_access_token(test_app, user_id)
#         headers = {
#                 "Authorization": f"Bearer {access_token}",
#         }
#         for key, value in additional_headers.items():
#             headers[key] = value

#         response = requests.get(
#             url=f"https://internal-dev.api.service.nhs.uk/{config.SERVICE_BASE_PATH}/user-role-service",
#             headers=headers
#         )

#         assert response.status_code == status_code

#     @pytest.mark.mock_auth
#     @pytest.mark.asyncio
#     @pytest.mark.parametrize("user_id,status_code,additional_headers,error_description", [
#         (
#             "656005750104",  # Multiple user roles found in userinfo
#             400,
#             {},
#             "multiple roles found in user info, please check nhsd-session-urid"
#         ),
#         (
#             "Aal3",  # No user role provided by any means
#             400,
#             {},
#             "no userroles available, please check nhsd-session-urid is valid"
#         ),
#         (
#             "Aal4",  # User role sent in id token but empty
#             400,
#             {},
#             "selected_roleid is misconfigured/invalid"
#         ),
#         (
#             "Aal5",  # nrbac is malformed, or person_roleid is empty (in userinfo)
#             400,
#             {},
#             "nhsid_nrbac_roles is misconfigured/invalid"
#         ),
#         (
#             "656005750104",  # Invalid role in header
#             400,
#             {"NHSD-Session-URID": "notAuserRole123"},
#             "nhsd-session-urid is invalid"
#         )
#     ])
#     async def test_user_role_unhappy_path(self, test_app_and_product,
#                                           user_id, status_code, additional_headers, error_description):
#         test_product, test_app = test_app_and_product
#         access_token = await self.get_access_token(test_app, user_id)
#         headers = {
#                 "Authorization": f"Bearer {access_token}",
#         }
#         for key, value in additional_headers.items():
#             headers[key] = value

#         response = requests.get(
#             url=f"https://internal-dev.api.service.nhs.uk/{config.SERVICE_BASE_PATH}/user-role-service",
#             headers=headers
#         )

#         assert response.status_code == status_code
#         assert response.json()["issue"][0]["diagnostics"] == error_description

#     @pytest.mark.simulated_auth
#     @pytest.mark.asyncio
#     @pytest.mark.parametrize("additional_headers,error_description", [
#         (
#             {},
#             "selected_roleid is missing in your token"
#         ),
#         (
#             {"NHSD-Session-URID": "656014452101"},
#             "unable to retrieve user info"
#         )
#     ])
#     async def test_nhs_login_exchanged_token_no_role_provided(
#             self,
#             get_token_nhs_login_token_exchange,
#             additional_headers,
#             error_description
#     ):
#         token = get_token_nhs_login_token_exchange["access_token"]
#         headers = {
#                 "Authorization": f"Bearer {token}",
#         }
#         for key, value in additional_headers.items():
#             headers[key] = value

#         response = requests.get(
#             url=f"https://internal-dev.api.service.nhs.uk/{config.SERVICE_BASE_PATH}/user-role-service",
#             headers=headers
#         )

#         assert response.status_code == 400
#         assert response.json()["issue"][0]["diagnostics"] == error_description

#     @pytest.mark.simulated_auth
#     @pytest.mark.asyncio
#     @pytest.mark.parametrize("additional_headers", [
#         (
#             {}
#         ),
#         (
#             {"NHSD-Session-URID": "656014452101"}
#         )
#     ])
#     async def test_cis2_exchanged_token_no_role_provided(
#             self,
#             get_token_cis2_token_exchange,
#             additional_headers
#     ):
#         token = get_token_cis2_token_exchange["access_token"]
#         headers = {
#                 "Authorization": f"Bearer {token}",
#         }
#         for key, value in additional_headers.items():
#             headers[key] = value

#         response = requests.get(
#             url=f"https://internal-dev.api.service.nhs.uk/{config.SERVICE_BASE_PATH}/user-role-service",
#             headers=headers
#         )

#         assert response.status_code == 200
