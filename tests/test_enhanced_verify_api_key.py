from os import getenv

import pytest
import requests


class TestEnhancedVerifyApiKey:
    """Test EnhancedVerifyApiKey Shared Flow"""

    def test_valid_api_key_products_subscribed(
        self,
        _create_function_scoped_test_app,
        _proxy_product_with_scope,
        nhsd_apim_proxy_url,
        nhsd_apim_config,
    ):
        # Create app
        app = _create_function_scoped_test_app

        app_name = app["name"]
        apikey = app["credentials"][0]["consumerKey"]
        email = nhsd_apim_config["APIGEE_DEVELOPER"]
        json_data = {
            "apiProducts": [
                _proxy_product_with_scope["name"]
            ]
        }
        url = (
            f"https://api.enterprise.apigee.com/v1/organizations/nhsd-nonprod/developers/"
            f"{email}/apps/{app_name}/keys/{apikey}"
        )

        access_token = getenv("APIGEE_ACCESS_TOKEN")

        # POST apiProducts to app
        update_proxy_resp = requests.post(
            url=url,
            json=json_data,
            headers={"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"},
            timeout=60
        )

        assert update_proxy_resp.status_code == 200

        proxy_resp = requests.get(
            url=f"{nhsd_apim_proxy_url}/enhanced-verify-api-key",
            headers={"apikey": apikey},
            timeout=60
        )

        assert proxy_resp.status_code == 200

    def test_valid_api_key_no_subscribed_products(
        self,
        _create_function_scoped_test_app,
        nhsd_apim_proxy_url,
    ):
        # Create test app and don't define any apiProducts
        app = _create_function_scoped_test_app
        apikey = app["credentials"][0]["consumerKey"]

        proxy_resp = requests.get(
            url=f"{nhsd_apim_proxy_url}/enhanced-verify-api-key",
            headers={"apikey": apikey},
            timeout=60
        )

        assert proxy_resp.status_code == 403

    def test_revoked_api_key(
        self,
        _create_function_scoped_test_app,
        nhsd_apim_proxy_url,
        nhsd_apim_config,
    ):
        app = _create_function_scoped_test_app
        app_name = app["name"]
        apikey = app["credentials"][0]["consumerKey"]
        email = nhsd_apim_config["APIGEE_DEVELOPER"]

        # Revoke credential
        url = (
            f"https://api.enterprise.apigee.com/v1/organizations/nhsd-nonprod/developers/"
            f"{email}/apps/{app_name}/keys/{apikey}?action=revoke"
        )

        access_token = getenv("APIGEE_ACCESS_TOKEN")
        update_proxy_resp = requests.post(
            url=url,
            headers={"Authorization": f"Bearer {access_token}"},
            timeout=60
        )

        assert update_proxy_resp.status_code == 204

        proxy_resp = requests.get(
            url=f"{nhsd_apim_proxy_url}/enhanced-verify-api-key",
            headers={"apikey": apikey},
            timeout=60
        )

        assert proxy_resp.status_code == 401

    @pytest.mark.parametrize("apikey, expected_status", [
        ("123", 401), ("abc", 401), ("123abc", 401)
    ])
    def test_invalid_api_key(
        self,
        nhsd_apim_proxy_url,
        expected_status,
        apikey,
    ):
        proxy_resp = requests.get(
            url=f"{nhsd_apim_proxy_url}/enhanced-verify-api-key",
            headers={"apikey": apikey},
            timeout=60
        )

        assert proxy_resp.status_code == expected_status
