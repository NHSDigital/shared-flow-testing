import json

import pytest
import requests

from .configuration.config import SERVICE_BASE_PATH, ENVIRONMENT


class TestSplunkLogging:
    url = f"https://{ENVIRONMENT}.api.service.nhs.uk/{SERVICE_BASE_PATH}/splunk-test"

    async def _get_auth_from_splunk_payload(self, debug):
        splunk_content_json = await debug.get_apigee_variable_from_trace(name='splunkCalloutRequest.content')
        return json.loads(splunk_content_json)["auth"]

    @pytest.mark.splunk
    @pytest.mark.asyncio
    @pytest.mark.debug
    async def test_splunk_auth_with_client_credentials(self, get_token_client_credentials, debug):
        # Given
        token = get_token_client_credentials["access_token"]

        # When
        await debug.start_trace()
        requests.get(
            url=self.url,
            headers={"Authorization": f"Bearer {token}"},
        )
        auth = await self._get_auth_from_splunk_payload(debug)

        # Then
        print(auth)

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
        auth = await self._get_auth_from_splunk_payload(debug)

        # Then
        print(auth)

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
        auth = await self._get_auth_from_splunk_payload(debug)

        # Then
        print(auth)

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
        auth = await self._get_auth_from_splunk_payload(debug)

        # Then
        print(auth)
