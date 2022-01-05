import uuid

import pytest
import requests
from api_test_utils.apigee_api_trace import ApigeeApiTraceDebug
from api_test_utils.oauth_helper import OauthHelper
from assertpy import assert_that

from .configuration import config


class TestExtendedAttributes:

    @pytest.mark.asyncio
    async def test_single_attribute(self, test_app_and_product, debug):
        # Given
        test_product, test_app = test_app_and_product
        await test_app.set_custom_attributes(
            {
                'jwks-resource-url': 'https://raw.githubusercontent.com/NHSDigital/'
                                     'identity-service-jwks/main/jwks/internal-dev/'
                                     '9baed6f4-1361-4a8e-8531-1f8426e3aba8.json',
                'apim-app-flow-vars': '{"proxy":{"allowed":{"update":true}}}'
            }
        )

        token = await self._get_auth_token(test_app)

        # When
        response = await self._send_request(token, debug)
        extended_attributes = await debug.get_apigee_variable_from_trace('app.apim-app-flow-vars')
        flow_variable = await debug.get_apigee_variable_from_trace('apim-app-flow-vars.proxy.allowed.update')

        # Then
        assert_that(200).is_equal_to(response.status_code)
        assert_that(extended_attributes).is_not_none()
        assert_that(extended_attributes).is_equal_to('{"proxy":{"allowed":{"update":true}}}')
        assert_that(extended_attributes).is_not_none()
        assert_that(flow_variable).is_equal_to('true')

    @pytest.mark.asyncio
    async def test_multiple_attributes(self, test_app_and_product, debug):
        # Given
        test_product, test_app = test_app_and_product
        await test_app.set_custom_attributes(
            {
                'jwks-resource-url': 'https://raw.githubusercontent.com/NHSDigital/'
                                     'identity-service-jwks/main/jwks/internal-dev/'
                                     '9baed6f4-1361-4a8e-8531-1f8426e3aba8.json',
                'apim-app-flow-vars': '{"attr_a": "value_a", "attr_b": "value_b"}'
            }
        )

        token = await self._get_auth_token(test_app)

        # When
        response = await self._send_request(token, debug)

        extended_attributes = await debug.get_apigee_variable_from_trace('app.apim-app-flow-vars')
        flow_variable_attr_a = await debug.get_apigee_variable_from_trace('apim-app-flow-vars.attr_a')
        flow_variable_attr_b = await debug.get_apigee_variable_from_trace('apim-app-flow-vars.attr_b')

        # Then
        assert_that(200).is_equal_to(response.status_code)
        assert_that(extended_attributes).is_not_none()
        assert_that(extended_attributes).is_equal_to('{"attr_a": "value_a", "attr_b": "value_b"}')
        assert_that(flow_variable_attr_a).is_not_none()
        assert_that(flow_variable_attr_a).is_equal_to('value_a')
        assert_that(flow_variable_attr_b).is_not_none()
        assert_that(flow_variable_attr_b).is_equal_to('value_b')

    @pytest.mark.asyncio
    async def test_no_attribute(self, test_app_and_product, debug):
        # Given
        test_product, test_app = test_app_and_product
        token = await self._get_auth_token(test_app)

        # When
        response = await self._send_request(token, debug)
        extended_attributes = await debug.get_apigee_variable_from_trace('app.apim-app-flow-vars')

        # Then
        assert_that(200).is_equal_to(response.status_code)
        assert_that(extended_attributes).is_empty()

    @pytest.mark.asyncio
    async def test_invalid_json(self, test_app_and_product, debug):
        # Given
        test_product, test_app = test_app_and_product
        await test_app.set_custom_attributes(
            {
                'jwks-resource-url': 'https://raw.githubusercontent.com/NHSDigital/'
                                     'identity-service-jwks/main/jwks/internal-dev/'
                                     '9baed6f4-1361-4a8e-8531-1f8426e3aba8.json',
                'apim-app-flow-vars': '{"proxy":{{"allowed":{"update":true}}}'
            }
        )

        token = await self._get_auth_token(test_app)

        # When
        response = await self._send_request(token, debug)
        raise_fault_var = await debug.get_apigee_variable_from_trace(
            'raisefault.RaiseFault.InvalidJson')  # is None unless the InvalidJson RaiseFault error has been thrown

        # Then
        assert_that(500).is_equal_to(response.status_code)
        assert_that(raise_fault_var).is_not_none()

    @staticmethod
    async def _send_request(token: str, debug: ApigeeApiTraceDebug):
        x_request_id_header = str(uuid.uuid4())
        debug.add_trace_filter(header_name='X-Request-ID', header_value=x_request_id_header)
        await debug.start_trace()

        return requests.get(
            url=f"https://internal-dev.api.service.nhs.uk/{config.SERVICE_BASE_PATH}/extended-attributes",
            headers={
                "Authorization": f"Bearer {token}",
                "NHSD-Session-URID": "555254242102",
                "X-Request-ID": x_request_id_header
            },
        )

    @staticmethod
    async def _get_auth_token(test_app):
        oauth = OauthHelper(
            client_id=test_app.client_id,
            client_secret=test_app.client_secret,
            redirect_uri=test_app.callback_url,
        )
        token_resp = await oauth.get_token_response(grant_type="authorization_code")
        assert token_resp["status_code"] == 200
        return token_resp["body"]["access_token"]
