import base64
import hashlib
import hmac
import json

import pytest
import requests
from jsonschema import validate

from .configuration.config import SERVICE_BASE_PATH, ENVIRONMENT, ACCESS_TOKEN_HASH_SECRET, APP_CLIENT_ID


class TestSplunkLogging:
    oauth_protected_url = f"https://{ENVIRONMENT}.api.service.nhs.uk/{SERVICE_BASE_PATH}/splunk-test"
    apikey_protected_url = f"https://{ENVIRONMENT}.api.service.nhs.uk/{SERVICE_BASE_PATH}/apikey-protected"
    open_access_url = f"https://{ENVIRONMENT}.api.service.nhs.uk/{SERVICE_BASE_PATH}/open-access"
    ping_url = f"https://{ENVIRONMENT}.api.service.nhs.uk/{SERVICE_BASE_PATH}/_ping"

    @staticmethod
    async def _get_payload_from_splunk(debug):
        splunk_content_json = await debug.get_apigee_variable_from_trace(name='splunkCalloutRequest.content')
        return json.loads(splunk_content_json)

    @staticmethod
    def _calculate_hmac_sha512(content: str) -> str:
        binary_content = bytes(content, "utf-8")
        hmac_key = bytes(ACCESS_TOKEN_HASH_SECRET, "utf-8")
        signature = hmac.new(hmac_key, binary_content, hashlib.sha512)

        return base64.b64encode(signature.digest()).decode("utf-8")

    @pytest.mark.simulated_auth
    @pytest.mark.splunk
    @pytest.mark.asyncio
    async def test_splunk_auth_with_client_credentials(self, get_token_client_credentials, debug):
        # Given
        token = get_token_client_credentials["access_token"]
        expected_hashed_token = self._calculate_hmac_sha512(token)

        # When
        await debug.start_trace()
        requests.get(
            url=self.oauth_protected_url,
            headers={"Authorization": f"Bearer {token}"},
        )
        payload = await self._get_payload_from_splunk(debug)

        # Then
        auth = payload["auth"]
        assert auth["access_token_hash"] == expected_hashed_token

        auth_meta = auth["meta"]
        assert auth_meta["auth_type"] == "app"
        assert auth_meta["grant_type"] == "client_credentials"
        assert auth_meta["level"] == "level3"
        assert auth_meta["provider"] == "apim"

        auth_user = auth["user"]
        assert auth_user["user_id"] == ""

    @pytest.mark.simulated_auth
    @pytest.mark.splunk
    @pytest.mark.asyncio
    async def test_splunk_auth_with_authorization_code(self, get_token, debug):
        # Given
        token = get_token["access_token"]
        expected_hashed_token = self._calculate_hmac_sha512(token)

        # When
        await debug.start_trace()
        requests.get(
            url=self.oauth_protected_url,
            headers={"Authorization": f"Bearer {token}"},
        )
        payload = await self._get_payload_from_splunk(debug)

        # Then
        auth = payload["auth"]
        assert auth["access_token_hash"] == expected_hashed_token

        auth_meta = auth["meta"]
        assert auth_meta["auth_type"] == "user"
        assert auth_meta["grant_type"] == "authorization_code"
        assert auth_meta["level"] == "aal3"
        assert auth_meta["provider"] == "nhs-cis2"

        auth_user = auth["user"]
        assert auth_user["user_id"] == "787807429511"

    @pytest.mark.simulated_auth
    @pytest.mark.splunk
    @pytest.mark.asyncio
    async def test_splunk_auth_with_cis2_token_exchange(self, get_token_cis2_token_exchange, debug):
        # Given
        token = get_token_cis2_token_exchange["access_token"]
        expected_hashed_token = self._calculate_hmac_sha512(token)

        # When
        await debug.start_trace()
        requests.get(
            url=self.oauth_protected_url,
            headers={"Authorization": f"Bearer {token}"},
        )
        payload = await self._get_payload_from_splunk(debug)

        # Then
        auth = payload["auth"]
        assert auth["access_token_hash"] == expected_hashed_token

        auth_meta = auth["meta"]
        assert auth_meta["auth_type"] == "user"
        assert auth_meta["grant_type"] == "token_exchange"
        assert auth_meta["level"] == "aal3"
        assert auth_meta["provider"] == "nhs-cis2"

        auth_user = auth["user"]
        assert auth_user["user_id"] == "lala"

    @pytest.mark.simulated_auth
    @pytest.mark.splunk
    @pytest.mark.asyncio
    async def test_splunk_auth_with_nhs_login_token_exchange(self, get_token_nhs_login_token_exchange, debug):
        # Given
        token = get_token_nhs_login_token_exchange["access_token"]
        expected_hashed_token = self._calculate_hmac_sha512(token)

        # When
        await debug.start_trace()
        requests.get(
            url=self.oauth_protected_url,
            headers={"Authorization": f"Bearer {token}"},
        )
        payload = await self._get_payload_from_splunk(debug)

        # Then
        auth = payload["auth"]
        assert auth["access_token_hash"] == expected_hashed_token

        auth_meta = auth["meta"]
        assert auth_meta["auth_type"] == "user"
        assert auth_meta["grant_type"] == "token_exchange"
        assert auth_meta["level"] == "p9"
        assert auth_meta["provider"] == "apim-mock-nhs-login"

        auth_user = auth["user"]
        assert auth_user["user_id"] == "900000000001"

    @pytest.mark.simulated_auth
    @pytest.mark.splunk
    @pytest.mark.asyncio
    async def test_splunk_auth_with_invalid_token(self, debug):
        # Given
        token = "invalid token"
        expected_hashed_token = "empty"

        # When
        await debug.start_trace()
        requests.get(
            url=self.oauth_protected_url,
            headers={"Authorization": f"Bearer {token}"},
        )
        payload = await self._get_payload_from_splunk(debug)

        # Then
        auth = payload["auth"]
        assert auth["access_token_hash"] == expected_hashed_token

        auth_meta = auth["meta"]
        assert auth_meta["auth_type"] == "unknown"
        assert auth_meta["grant_type"] == ""
        assert auth_meta["level"] == "-"
        assert auth_meta["provider"] == "apim"

        auth_user = auth["user"]
        assert auth_user["user_id"] == ""

        meta = payload["meta"]
        assert meta["client_id"] == "empty"
        assert meta["application"] == "unknown"
        assert meta["product"] == ""

    @pytest.mark.simulated_auth
    @pytest.mark.splunk
    @pytest.mark.asyncio
    async def test_splunk_auth_with_expired_token(self, debug):
        # Given
        token = "zRygtc34R2pwxbiUktLsMJWX0iJW"
        expected_hashed_token = "empty"

        # When
        await debug.start_trace()
        requests.get(
            url=self.oauth_protected_url,
            headers={"Authorization": f"Bearer {token}"},
        )
        payload = await self._get_payload_from_splunk(debug)

        # Then
        auth = payload["auth"]
        assert auth["access_token_hash"] == expected_hashed_token

        auth_meta = auth["meta"]
        assert auth_meta["auth_type"] == "unknown"
        assert auth_meta["grant_type"] == ""
        assert auth_meta["level"] == "-"
        assert auth_meta["provider"] == "apim"

        auth_user = auth["user"]
        assert auth_user["user_id"] == ""

        meta = payload["meta"]
        assert meta["client_id"] == "empty"
        assert meta["application"] == "unknown"
        assert meta["product"] == ""

    @pytest.mark.simulated_auth
    @pytest.mark.splunk
    @pytest.mark.asyncio
    async def test_splunk_auth_with_apikey(self, debug):
        # Given
        apikey = APP_CLIENT_ID

        # When
        await debug.start_trace()
        requests.get(
            url=self.apikey_protected_url,
            headers={"apikey": apikey},
        )
        payload = await self._get_payload_from_splunk(debug)

        # Then
        auth = payload["auth"]
        assert auth["access_token_hash"] == ""

        auth_meta = auth["meta"]
        assert auth_meta["auth_type"] == "app"
        assert auth_meta["grant_type"] == ""
        assert auth_meta["level"] == "-"
        assert auth_meta["provider"] == "apim"

        auth_user = auth["user"]
        assert auth_user["user_id"] == ""

        meta = payload["meta"]
        assert meta["client_id"] == apikey

    @pytest.mark.simulated_auth
    @pytest.mark.splunk
    @pytest.mark.asyncio
    async def test_splunk_auth_with_invalid_apikey(self, debug):
        # Given
        apikey = "invalid api key"

        # When
        await debug.start_trace()
        requests.get(
            url=self.apikey_protected_url,
            headers={"apikey": apikey},
        )
        payload = await self._get_payload_from_splunk(debug)

        # Then
        auth = payload["auth"]
        assert auth["access_token_hash"] == ""

        auth_meta = auth["meta"]
        assert auth_meta["auth_type"] == "app"
        assert auth_meta["grant_type"] == ""
        assert auth_meta["level"] == "-"
        assert auth_meta["provider"] == "apim"

        auth_user = auth["user"]
        assert auth_user["user_id"] == ""

        meta = payload["meta"]
        assert meta["client_id"] == ""
        assert meta["application"] == "unknown"
        assert meta["product"] == ""

    @pytest.mark.simulated_auth
    @pytest.mark.splunk
    @pytest.mark.asyncio
    async def test_splunk_auth_open_access(self, debug):
        # When
        await debug.start_trace()
        requests.get(
            url=self.open_access_url,
        )
        payload = await self._get_payload_from_splunk(debug)

        # Then
        auth = payload["auth"]
        assert auth["access_token_hash"] == ""

        auth_meta = auth["meta"]
        assert auth_meta["auth_type"] == "app"
        assert auth_meta["grant_type"] == ""
        assert auth_meta["level"] == "open"
        assert auth_meta["provider"] == "apim"

        auth_user = auth["user"]
        assert auth_user["user_id"] == ""

        meta = payload["meta"]
        assert meta["client_id"] == "empty"
        assert meta["application"] == "unknown"

    @pytest.mark.simulated_auth
    @pytest.mark.splunk
    @pytest.mark.asyncio
    async def test_splunk_auth_open_access_ping(self, debug):
        # There is nothing especial about /_ping itself. It's an endpoint that doesn't have a target backend
        # When
        await debug.start_trace()
        requests.get(
            url=self.ping_url,
        )
        payload = await self._get_payload_from_splunk(debug)

        # Then
        auth = payload["auth"]
        assert auth["access_token_hash"] == ""

        auth_meta = auth["meta"]
        assert auth_meta["auth_type"] == "app"
        assert auth_meta["grant_type"] == ""
        assert auth_meta["level"] == "open"
        assert auth_meta["provider"] == "apim"

        auth_user = auth["user"]
        assert auth_user["user_id"] == ""

        meta = payload["meta"]
        assert meta["client_id"] == "empty"
        assert meta["application"] == "unknown"

    @pytest.mark.simulated_auth
    @pytest.mark.splunk
    @pytest.mark.asyncio
    async def test_splunk_payload_schema(self, get_token, debug):
        # Given
        token = get_token["access_token"]

        # When
        await debug.start_trace()
        requests.get(
            url=self.oauth_protected_url,
            headers={"Authorization": f"Bearer {token}"},
        )
        payload = await self._get_payload_from_splunk(debug)

        with open('splunk_logging_schema.json') as f:
            schema = json.load(f)

        # If no exception is raised by validate(), the instance is valid.
        validate(instance=payload, schema=schema)

    @pytest.mark.simulated_auth
    @pytest.mark.splunk
    @pytest.mark.asyncio
    async def test_splunk_payload_schema_open_access(self, debug):
        # When hitting an open-access endpoint
        await debug.start_trace()
        requests.get(url=self.open_access_url)
        payload = await self._get_payload_from_splunk(debug)

        with open('splunk_logging_schema.json') as f:
            schema = json.load(f)

        # Then
        # If no exception is raised by validate(), the instance is valid.
        validate(instance=payload, schema=schema)
