from os import getenv

import pytest
import requests


class TestEnhancedVerifyApiKey:
    """Test EnhancedVerifyApiKey Shared Flow"""

    @pytest.mark.parametrize("expected_status_code", [(200)])
    def test_valid_api_key_products_subscribed(
        self,
        _create_function_scoped_test_app,
        _proxy_product_with_scope,
        nhsd_apim_proxy_url,
        nhsd_apim_config,
        expected_status_code
    ):
        # Create app with products
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
        update_app_resp = requests.post(
            url=url,
            json=json_data,
            headers={"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"},
            timeout=60
        )

        assert update_app_resp.status_code == expected_status_code

        proxy_resp = requests.get(
            url=f"{nhsd_apim_proxy_url}/enhanced-verify-api-key",
            headers={"apikey": apikey},
            timeout=60
        )

        assert proxy_resp.status_code == expected_status_code

    @pytest.mark.parametrize("expected_status_code", [(403)])
    def test_valid_api_key_no_subscribed_products(
        self,
        _create_function_scoped_test_app,
        nhsd_apim_proxy_url,
        expected_status_code
    ):
        # Create test app and don't define any apiProducts
        app = _create_function_scoped_test_app
        apikey = app["credentials"][0]["consumerKey"]

        proxy_resp = requests.get(
            url=f"{nhsd_apim_proxy_url}/enhanced-verify-api-key",
            headers={"apikey": apikey},
            timeout=60
        )

        assert proxy_resp.status_code == expected_status_code

    @pytest.mark.parametrize("expected_status_code", [(401)])
    def test_revoked_api_key(
        self,
        _create_function_scoped_test_app,
        nhsd_apim_proxy_url,
        nhsd_apim_config,
        expected_status_code
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
        update_app_resp = requests.post(
            url=url,
            headers={"Authorization": f"Bearer {access_token}"},
            timeout=60
        )

        expected_resp = [200, 204]
        assert update_app_resp.status_code in expected_resp

        proxy_resp = requests.get(
            url=f"{nhsd_apim_proxy_url}/enhanced-verify-api-key",
            headers={"apikey": apikey},
            timeout=60
        )

        assert proxy_resp.status_code == expected_status_code

    @pytest.mark.parametrize("apikey, expected_status_code", [
        ("123", 401), ("abc", 401), ("123abc", 401)
    ])
    def test_invalid_api_key(
        self,
        nhsd_apim_proxy_url,
        expected_status_code,
        apikey,
    ):
        proxy_resp = requests.get(
            url=f"{nhsd_apim_proxy_url}/enhanced-verify-api-key",
            headers={"apikey": apikey},
            timeout=60
        )

        assert proxy_resp.status_code == expected_status_code

    @pytest.mark.parametrize("expected_status_code", [(401)])
    def test_valid_api_key_incorrect_product(
        self,
        _create_function_scoped_test_app,
        nhsd_apim_proxy_url,
        nhsd_apim_config,
        expected_status_code
    ):
        # Create app with an incorrect product
        app = _create_function_scoped_test_app
        app_name = app["name"]
        apikey = app["credentials"][0]["consumerKey"]
        email = nhsd_apim_config["APIGEE_DEVELOPER"]
        json_data = {
            "apiProducts": [
                "hello-world-internal-dev"
            ]
        }
        url = (
            f"https://api.enterprise.apigee.com/v1/organizations/nhsd-nonprod/developers/"
            f"{email}/apps/{app_name}/keys/{apikey}"
        )

        access_token = getenv("APIGEE_ACCESS_TOKEN")

        # POST apiProducts to app
        update_app_resp = requests.post(
            url=url,
            json=json_data,
            headers={"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"},
            timeout=60
        )

        assert update_app_resp.status_code == 200

        proxy_resp = requests.get(
            url=f"{nhsd_apim_proxy_url}/enhanced-verify-api-key",
            headers={"apikey": apikey},
            timeout=60
        )

        assert proxy_resp.status_code == expected_status_code
