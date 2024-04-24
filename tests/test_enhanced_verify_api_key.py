from uuid import uuid4
import pytest
import requests


class TestEnhancedVerifyApiKey():
    """Test enhanced verify api key policy"""

    @pytest
    def test_valid_api_key_products_subscribed(
        self,
        nhsd_apim_proxy_url,
        _create_function_scoped_test_app,
        _proxy_product_with_scope,
        developer_apps_api,
        nhsd_apim_config,
        trace,
        new_attribute,
    ):

        # Update test app with proxy product and the extended attribute
        app = _create_function_scoped_test_app
        app["apiProducts"] = [_proxy_product_with_scope["name"]]
        app["attributes"].append(new_attribute)
        app = developer_apps_api.put_app_by_name(
            email=nhsd_apim_config["APIGEE_DEVELOPER"], app_name=app["name"], body=app
        )

        # Trace call to shared flow proxy enhanced verify apikey endpoint
        session_name = str(uuid4())
        header_filters = {"trace_id": session_name}
        trace.post_debugsession(session=session_name, header_filters=header_filters)

        apikey = app["credentials"][0]["consumerKey"],

        proxy_resp = requests.get(
            url=f"{nhsd_apim_proxy_url}/enhanced-verify-api-key",
            headers={"apikey": apikey, **header_filters},
        )
        assert proxy_resp.status_code == 200

        trace.delete_debugsession_by_name(session_name)

    @pytest
    def test_valid_api_key_no_products_subscribed(
        self,
        nhsd_apim_proxy_url,
        _create_function_scoped_test_app,
        developer_apps_api,
        nhsd_apim_config,
        trace,
        new_attribute,
    ):

        # Update test app with proxy product and the extended attribute
        app = _create_function_scoped_test_app
        app["apiProducts"] = []
        app["attributes"].append(new_attribute)
        app = developer_apps_api.put_app_by_name(
            email=nhsd_apim_config["APIGEE_DEVELOPER"], app_name=app["name"], body=app
        )

        # Trace call to shared flow proxy enhanced verify apikey endpoint
        session_name = str(uuid4())
        header_filters = {"trace_id": session_name}
        trace.post_debugsession(session=session_name, header_filters=header_filters)

        apikey = app["credentials"][0]["consumerKey"],

        proxy_resp = requests.get(
            url=f"{nhsd_apim_proxy_url}/enhanced-verify-api-key",
            headers={"apikey": apikey, **header_filters},
        )
        assert proxy_resp.status_code == 403

        trace.delete_debugsession_by_name(session_name)

    @pytest
    def test_revoked_api_key_products_subscribed(
        self,
        nhsd_apim_proxy_url,
        _create_function_scoped_test_app,
        _proxy_product_with_scope,
        developer_apps_api,
        nhsd_apim_config,
        trace,
        new_attribute,
    ):

        # Update test app with proxy product and the extended attribute
        app = _create_function_scoped_test_app
        app["apiProducts"] = [_proxy_product_with_scope["name"]]
        app["attributes"].append(new_attribute)
        app = developer_apps_api.put_app_by_name(
            email=nhsd_apim_config["APIGEE_DEVELOPER"], app_name=app["name"], body=app
        )

        # Trace call to shared flow proxy enhanced verify apikey endpoint
        session_name = str(uuid4())
        header_filters = {"trace_id": session_name}
        trace.post_debugsession(session=session_name, header_filters=header_filters)

        app["credentials"][0]["status"] = "revoked"
        apikey = app["credentials"][0]["consumerKey"],

        proxy_resp = requests.get(
            url=f"{nhsd_apim_proxy_url}/enhanced-verify-api-key",
            headers={"apikey": apikey, **header_filters},
        )
        assert proxy_resp.status_code == 401

        trace.delete_debugsession_by_name(session_name)

    @pytest
    def test_revoked_api_key_no_products_subscribed(
        self,
        nhsd_apim_proxy_url,
        _create_function_scoped_test_app,
        developer_apps_api,
        nhsd_apim_config,
        trace,
        new_attribute,
    ):

        # Update test app with proxy product and the extended attribute
        app = _create_function_scoped_test_app
        app["apiProducts"] = []
        app["attributes"].append(new_attribute)
        app = developer_apps_api.put_app_by_name(
            email=nhsd_apim_config["APIGEE_DEVELOPER"], app_name=app["name"], body=app
        )

        # Trace call to shared flow proxy enhanced verify apikey endpoint
        session_name = str(uuid4())
        header_filters = {"trace_id": session_name}
        trace.post_debugsession(session=session_name, header_filters=header_filters)

        app["credentials"][0]["status"] = "revoked"
        apikey = app["credentials"][0]["consumerKey"],

        proxy_resp = requests.get(
            url=f"{nhsd_apim_proxy_url}/enhanced-verify-api-key",
            headers={"apikey": apikey, **header_filters},
        )
        assert proxy_resp.status_code == 401

        trace.delete_debugsession_by_name(session_name)

    @pytest
    def test_invalid_api_key(
        self,
        nhsd_apim_proxy_url,
        _create_function_scoped_test_app,
        developer_apps_api,
        nhsd_apim_config,
        trace,
        new_attribute,
    ):

        # Update test app with proxy product and the extended attribute
        app = _create_function_scoped_test_app
        app["apiProducts"] = []
        app["attributes"].append(new_attribute)
        app = developer_apps_api.put_app_by_name(
            email=nhsd_apim_config["APIGEE_DEVELOPER"], app_name=app["name"], body=app
        )

        # Trace call to shared flow proxy enhanced verify apikey endpoint
        session_name = str(uuid4())
        header_filters = {"trace_id": session_name}
        trace.post_debugsession(session=session_name, header_filters=header_filters)

        apikey = "invalidapikey123"
        proxy_resp = requests.get(
            url=f"{nhsd_apim_proxy_url}/enhanced-verify-api-key",
            headers={"apikey": apikey, **header_filters},
        )
        assert proxy_resp.status_code == 401

        trace.delete_debugsession_by_name(session_name)
