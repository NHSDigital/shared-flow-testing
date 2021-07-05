import json
import pytest
import requests

from .configuration.config import SERVICE_BASE_PATH, ENVIRONMENT
from jsonschema import validate


class TestSplunkLogging:
    url = f"https://{ENVIRONMENT}.api.service.nhs.uk/{SERVICE_BASE_PATH}/splunk-test"

    async def _get_payload_from_splunk(self, debug):
        splunk_content_json = await debug.get_apigee_variable_from_trace(name='splunkCalloutRequest.content')
        return json.loads(splunk_content_json)

    @pytest.mark.splunk
    @pytest.mark.asyncio
    async def test_splunk_auth_with_client_credentials(self, get_token_client_credentials, debug):
        # Given
        token = get_token_client_credentials["access_token"]

        # When
        await debug.start_trace()
        requests.get(
            url=self.url,
            headers={"Authorization": f"Bearer {token}"},
        )
        payload = await self._get_payload_from_splunk(debug)
        auth = payload["auth"]["meta"]

        # Then
        assert auth["auth_type"] == "app"
        assert auth["grant_type"] == "client_credentials"
        assert auth["level"] == "level3"
        assert auth["provider"] == "apim"

    @pytest.mark.splunk
    @pytest.mark.asyncio
    async def test_splunk_auth_with_authorization_code(self, get_token, debug):
        # Given
        token = get_token["access_token"]

        # When
        await debug.start_trace()
        requests.get(
            url=self.url,
            headers={"Authorization": f"Bearer {token}"},
        )
        payload = await self._get_payload_from_splunk(debug)
        auth = payload["auth"]["meta"]

        # Then
        assert auth["auth_type"] == "user"
        assert auth["grant_type"] == "authorization_code"
        assert auth["level"] == "aal3"
        assert auth["provider"] == "nhs-cis2"

    @pytest.mark.splunk
    @pytest.mark.asyncio
    async def test_splunk_auth_with_cis2_token_exchange(self, get_token_cis2_token_exchange, debug):
        # Given
        token = get_token_cis2_token_exchange["access_token"]

        # When
        await debug.start_trace()
        requests.get(
            url=self.url,
            headers={"Authorization": f"Bearer {token}"},
        )
        payload = await self._get_payload_from_splunk(debug)
        auth = payload["auth"]["meta"]

        # Then
        assert auth["auth_type"] == "user"
        assert auth["grant_type"] == "token_exchange"
        assert auth["level"] == "aal3"
        assert auth["provider"] == "nhs-cis2"

    @pytest.mark.splunk
    @pytest.mark.asyncio
    async def test_splunk_auth_with_nhs_login_token_exchange(self, get_token_nhs_login_token_exchange, debug):
        # Given
        token = get_token_nhs_login_token_exchange["access_token"]

        # When
        await debug.start_trace()
        requests.get(
            url=self.url,
            headers={"Authorization": f"Bearer {token}"},
        )
        payload = await self._get_payload_from_splunk(debug)
        auth = payload["auth"]["meta"]

        # Then

        assert auth["auth_type"] == "user"
        assert auth["grant_type"] == "token_exchange"
        assert auth["level"] == "p9"
        assert auth["provider"] == "nhs-login"

    @pytest.mark.splunk
    @pytest.mark.asyncio
    async def test_splunk_payload(self, get_token, debug):

        # Given
        token = get_token["access_token"]

        # When
        await debug.start_trace()
        requests.get(
            url=self.url,
            headers={"Authorization": f"Bearer {token}"},
        )
        payload = await self._get_payload_from_splunk(debug)

        with open('splunk_logging_schema.json') as f:
            schema = json.load(f)

        # If no exception is raised by validate(), the instance is valid.
        validate(instance=payload, schema=schema)
