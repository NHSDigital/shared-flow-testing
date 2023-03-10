import base64
import hashlib
import hmac
import json
import pytest
import requests

from jsonschema import validate
from uuid import uuid4

from tests.utils.config import ENV
from tests.utils.helpers import get_variable_from_trace


class TestSplunkLogging:
    """Test attributes are logged to splunk"""

    @staticmethod
    def _calculate_hmac_sha512(content: str) -> str:
        binary_content = bytes(content, "utf-8")
        hmac_key = bytes(ENV["access_token_hash_secret"], "utf-8")
        signature = hmac.new(hmac_key, binary_content, hashlib.sha512)

        return base64.b64encode(signature.digest()).decode("utf-8")

    # @pytest.mark.nhsd_apim_authorization(
    #     access="healthcare_worker",
    #     level="aal3",
    #     login_form={"username": "656005750104"},
    #     force_new_token=True,
    # )
    # def test_splunk_payload_schema(
    #     self,
    #     nhsd_apim_auth_headers,
    #     nhsd_apim_proxy_url,
    #     trace,
    # ):
    #     session_name = str(uuid4())
    #     header_filters = {"trace_id": session_name}
    #     trace.post_debugsession(session=session_name, header_filters=header_filters)

    #     requests.get(
    #         url=f"{nhsd_apim_proxy_url}/splunk-test",
    #         headers={**nhsd_apim_auth_headers, **header_filters},
    #     )

    #     payload = json.loads(
    #         get_variable_from_trace(trace, session_name, "splunkCalloutRequest.content")
    #     )

    #     trace.delete_debugsession_by_name(session_name)

    #     with open("tests/utils/splunk_logging_schema.json") as f:
    #         schema = json.load(f)

    #     # If no exception is raised by validate(), the instance is valid.
    #     validate(instance=payload, schema=schema)

    # def test_splunk_payload_schema_open_access(
    #     self,
    #     nhsd_apim_proxy_url,
    #     trace,
    # ):
    #     session_name = str(uuid4())
    #     header_filters = {"trace_id": session_name}
    #     trace.post_debugsession(session=session_name, header_filters=header_filters)

    #     requests.get(
    #         url=f"{nhsd_apim_proxy_url}/open-access",
    #         headers=header_filters,
    #     )

    #     payload = json.loads(
    #         get_variable_from_trace(trace, session_name, "splunkCalloutRequest.content")
    #     )

    #     trace.delete_debugsession_by_name(session_name)

    #     with open("tests/utils/splunk_logging_schema.json") as f:
    #         schema = json.load(f)

    #     # If no exception is raised by validate(), the instance is valid.
    #     validate(instance=payload, schema=schema)

    # @pytest.mark.parametrize(
    #     "expected_attr",
    #     [
    #         pytest.param(
    #             {
    #                 "auth_type": "app",
    #                 "grant_type": "client_credentials",
    #                 "level": "level3",
    #                 "provider": "apim",
    #                 "user_id": "",
    #             },
    #             marks=pytest.mark.nhsd_apim_authorization(
    #                 access="application", level="level3", force_new_token=True
    #             ),
    #             id="Client credentials",
    #         ),
    #         pytest.param(
    #             {
    #                 "auth_type": "user",
    #                 "grant_type": "authorization_code",
    #                 "level": "aal3",
    #                 "provider": "apim-mock-nhs-cis2",
    #                 "user_id": "656005750104",
    #             },
    #             marks=pytest.mark.nhsd_apim_authorization(
    #                 access="healthcare_worker",
    #                 level="aal3",
    #                 login_form={"username": "656005750104"},
    #                 force_new_token=True,
    #             ),
    #             id="Authorization Code: CIS2",
    #         ),
    #         pytest.param(
    #             {
    #                 "auth_type": "user",
    #                 "grant_type": "authorization_code",
    #                 "level": "p9",
    #                 "provider": "apim-mock-nhs-login",
    #                 "user_id": "9912003071",
    #             },
    #             marks=pytest.mark.nhsd_apim_authorization(
    #                 access="patient",
    #                 level="P9",
    #                 login_form={"username": "9912003071"},
    #                 force_new_token=True,
    #             ),
    #             id="Authorization Code: NHS Login",
    #         ),
    #         pytest.param(
    #             {
    #                 "auth_type": "user",
    #                 "grant_type": "token_exchange",
    #                 "level": "aal3",
    #                 "provider": "apim-mock-nhs-cis2",
    #                 "user_id": "656005750104",
    #             },
    #             marks=pytest.mark.nhsd_apim_authorization(
    #                 access="healthcare_worker",
    #                 level="aal3",
    #                 login_form={"username": "656005750104"},
    #                 authentication="separate",
    #                 force_new_token=True,
    #             ),
    #             id="Token exchange: CIS2",
    #         ),
    #         pytest.param(
    #             {
    #                 "auth_type": "user",
    #                 "grant_type": "token_exchange",
    #                 "level": "p9",
    #                 "provider": "apim-mock-nhs-login",
    #                 "user_id": "9912003071",
    #             },
    #             marks=pytest.mark.nhsd_apim_authorization(
    #                 access="patient",
    #                 level="P9",
    #                 login_form={"username": "9912003071"},
    #                 authentication="separate",
    #                 force_new_token=True,
    #             ),
    #             id="Token exchange: NHS Login",
    #         ),
    #     ],
    # )
    # def test_splunk_auth_attributes(
    #     self, _nhsd_apim_auth_token_data, nhsd_apim_proxy_url, trace, expected_attr
    # ):
    #     access_token = _nhsd_apim_auth_token_data["access_token"]
    #     expected_hashed_token = self._calculate_hmac_sha512(access_token)

    #     session_name = str(uuid4())
    #     header_filters = {"trace_id": session_name}
    #     trace.post_debugsession(session=session_name, header_filters=header_filters)

    #     requests.get(
    #         url=f"{nhsd_apim_proxy_url}/splunk-test",
    #         headers={"Authorization": f"Bearer {access_token}", **header_filters},
    #     )

    #     payload = json.loads(
    #         get_variable_from_trace(trace, session_name, "splunkCalloutRequest.content")
    #     )

    #     trace.delete_debugsession_by_name(session_name)

    #     auth = payload["auth"]
    #     assert auth["access_token_hash"] == expected_hashed_token

    #     auth_meta = auth["meta"]
    #     assert auth_meta["auth_type"] == expected_attr["auth_type"]
    #     assert auth_meta["grant_type"] == expected_attr["grant_type"]
    #     assert auth_meta["level"] == expected_attr["level"]
    #     assert auth_meta["provider"] == expected_attr["provider"]

    #     auth_user = auth["user"]
    #     assert auth_user["user_id"] == expected_attr["user_id"]

    # @pytest.mark.nhsd_apim_authorization(
    #     access="application", level="level0", force_new_token=True
    # )
    # def test_splunk_auth_attributes_api_key(
    #     self,
    #     _nhsd_apim_auth_token_data,
    #     nhsd_apim_proxy_url,
    #     trace,
    # ):
    #     api_key = _nhsd_apim_auth_token_data["apikey"]

    #     session_name = str(uuid4())
    #     header_filters = {"trace_id": session_name}
    #     trace.post_debugsession(session=session_name, header_filters=header_filters)

    #     requests.get(
    #         url=f"{nhsd_apim_proxy_url}/apikey-protected",
    #         headers={"apikey": api_key, **header_filters},
    #     )

    #     payload = json.loads(
    #         get_variable_from_trace(trace, session_name, "splunkCalloutRequest.content")
    #     )

    #     trace.delete_debugsession_by_name(session_name)

    #     auth = payload["auth"]
    #     assert auth["access_token_hash"] == ""

    #     auth_meta = auth["meta"]
    #     assert auth_meta["auth_type"] == "app"
    #     assert auth_meta["grant_type"] == ""
    #     assert auth_meta["level"] == "-"
    #     assert auth_meta["provider"] == "apim"

    #     auth_user = auth["user"]
    #     assert auth_user["user_id"] == ""

    #     meta = payload["meta"]
    #     assert meta["client_id"] == api_key

    # def test_splunk_auth_attributes_invalid_api_key(
    #     self,
    #     nhsd_apim_proxy_url,
    #     trace,
    # ):
    #     api_key = "invalid api key"

    #     session_name = str(uuid4())
    #     header_filters = {"trace_id": session_name}
    #     trace.post_debugsession(session=session_name, header_filters=header_filters)

    #     requests.get(
    #         url=f"{nhsd_apim_proxy_url}/apikey-protected",
    #         headers={"apikey": api_key, **header_filters},
    #     )

    #     payload = json.loads(
    #         get_variable_from_trace(trace, session_name, "splunkCalloutRequest.content")
    #     )

    #     trace.delete_debugsession_by_name(session_name)

    #     auth = payload["auth"]
    #     assert auth["access_token_hash"] == ""

    #     auth_meta = auth["meta"]
    #     assert auth_meta["auth_type"] == "app"
    #     assert auth_meta["grant_type"] == ""
    #     assert auth_meta["level"] == "-"
    #     assert auth_meta["provider"] == "apim"

    #     auth_user = auth["user"]
    #     assert auth_user["user_id"] == ""

    #     meta = payload["meta"]
    #     assert meta["client_id"] == ""
    #     assert meta["application"] == "unknown"
    #     assert meta["product"] == ""

    # @pytest.mark.parametrize("endpoint", ["/open-access", "/_ping"])
    # def test_splunk_attributes_open_access(self, nhsd_apim_proxy_url, trace, endpoint):
    #     session_name = str(uuid4())
    #     header_filters = {"trace_id": session_name}
    #     trace.post_debugsession(session=session_name, header_filters=header_filters)

    #     requests.get(
    #         url=nhsd_apim_proxy_url + endpoint,
    #         headers=header_filters,
    #     )

    #     payload = json.loads(
    #         get_variable_from_trace(trace, session_name, "splunkCalloutRequest.content")
    #     )

    #     trace.delete_debugsession_by_name(session_name)

    #     auth = payload["auth"]
    #     assert auth["access_token_hash"] == ""

    #     auth_meta = auth["meta"]
    #     assert auth_meta["auth_type"] == "app"
    #     assert auth_meta["grant_type"] == ""
    #     assert auth_meta["level"] == "open"
    #     assert auth_meta["provider"] == "apim"

    #     auth_user = auth["user"]
    #     assert auth_user["user_id"] == ""

    #     meta = payload["meta"]
    #     assert meta["client_id"] == "empty"
    #     assert meta["application"] == "unknown"

    # @pytest.mark.parametrize(
    #     "access_token",
    #     [
    #         pytest.param("invalid token", id="Invalid token"),
    #         pytest.param("zRygtc34R2pwxbiUktLsMJWX0iJW", id="Expired token"),
    #     ],
    # )
    # def test_splunk_auth_attributes_invalid_token(
    #     self, access_token, nhsd_apim_proxy_url, trace
    # ):
    #     expected_hashed_token = "empty"

    #     session_name = str(uuid4())
    #     header_filters = {"trace_id": session_name}
    #     trace.post_debugsession(session=session_name, header_filters=header_filters)

    #     requests.get(
    #         url=f"{nhsd_apim_proxy_url}/splunk-test",
    #         headers={"Authorization": f"Bearer {access_token}", **header_filters},
    #     )

    #     payload = json.loads(
    #         get_variable_from_trace(trace, session_name, "splunkCalloutRequest.content")
    #     )

    #     trace.delete_debugsession_by_name(session_name)

    #     auth = payload["auth"]
    #     assert auth["access_token_hash"] == expected_hashed_token

    #     auth_meta = auth["meta"]
    #     assert auth_meta["auth_type"] == "unknown"
    #     assert auth_meta["grant_type"] == ""
    #     assert auth_meta["level"] == "-"
    #     assert auth_meta["provider"] == "apim"

    #     auth_user = auth["user"]
    #     assert auth_user["user_id"] == ""

    #     meta = payload["meta"]
    #     assert meta["client_id"] == "empty"
    #     assert meta["application"] == "unknown"
    #     assert meta["product"] == ""

    @pytest.mark.nhsd_apim_authorization(
        access="application", level="level3", force_new_token=True
    )
    @pytest.mark.parametrize("message_type", ["request", "response"])
    def test_splunk_not_allowed_headers(
        self, _nhsd_apim_auth_token_data, nhsd_apim_proxy_url, trace, message_type
    ):
        access_token = _nhsd_apim_auth_token_data["access_token"]

        session_name = str(uuid4())
        header_filters = {"trace_id": session_name}
        trace.post_debugsession(session=session_name, header_filters=header_filters)

        requests.get(
            url=f"{nhsd_apim_proxy_url}/splunk-test",
            headers={"Authorization": f"Bearer {access_token}", **header_filters},
        )

        payload = json.loads(
            get_variable_from_trace(trace, session_name, "splunkCalloutRequest.content")
        )

        trace.delete_debugsession_by_name(session_name)

        content = payload[message_type]
        assert content["headers"]

        headers = json.loads(content["headers"])

        deny_list = ["Authorization", "Cookie", "User-Agent"]
        for denied_header in deny_list:
            assert denied_header not in headers
