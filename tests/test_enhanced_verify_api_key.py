from uuid import uuid4
import pytest
import requests


@pytest.fixture
def create_test_app(
    _create_function_scoped_test_app,
    developer_apps_api,
    nhsd_apim_config,
):
    """Fixture for creating test app"""

    app = _create_function_scoped_test_app
    app = developer_apps_api.put_app_by_name(
        email=nhsd_apim_config["APIGEE_DEVELOPER"], app_name=app["name"], body=app
    )
    return app


@pytest.fixture
def tracing(trace):
    """Fixture for tracing setup and teardown"""

    session_name = str(uuid4())
    header_filters = {"trace_id": session_name}
    trace.post_debugsession(session=session_name, header_filters=header_filters)
    yield session_name, header_filters
    trace.delete_debugsession_by_name(session_name)


def test_valid_api_key_products_subscribed(
    nhsd_apim_proxy_url,
    create_test_app,
    tracing,
    _proxy_product_with_scope,
):
    session_name, header_filters = tracing
    apikey = create_test_app["credentials"][0]["consumerKey"]
    create_test_app["apiProducts"] = [_proxy_product_with_scope['name']]

    proxy_resp = requests.get(
        url=f"{nhsd_apim_proxy_url}/enhanced-verify-api-key",
        headers={"apikey": apikey, **header_filters},
    )

    assert proxy_resp.status_code == 200


def test_valid_api_key_no_subscribed_products(
    nhsd_apim_proxy_url,
    create_test_app,
    tracing,
):
    session_name, header_filters = tracing
    apikey = create_test_app["credentials"][0]["consumerKey"]
    create_test_app["apiProducts"] = []

    proxy_resp = requests.get(
        url=f"{nhsd_apim_proxy_url}/enhanced-verify-api-key",
        headers={"apikey": apikey, **header_filters},
    )

    assert proxy_resp.status_code == 403


def test_revoked_api_key(
    nhsd_apim_proxy_url,
    create_test_app,
    tracing,
    _proxy_product_with_scope,
):
    session_name, header_filters = tracing
    apikey = create_test_app["credentials"][0]["consumerKey"]
    create_test_app["apiProducts"] = [_proxy_product_with_scope['name']]
    create_test_app["credentials"][0]["status"] = "revoked"

    proxy_resp = requests.get(
        url=f"{nhsd_apim_proxy_url}/enhanced-verify-api-key",
        headers={"apikey": apikey, **header_filters},
    )

    assert proxy_resp.status_code == 401


def test_invalid_api_key(
    nhsd_apim_proxy_url,
    create_test_app,
    tracing
):
    session_name, header_filters = tracing
    apikey = "123"

    proxy_resp = requests.get(
        url=f"{nhsd_apim_proxy_url}/enhanced-verify-api-key",
        headers={"apikey": apikey, **header_filters},
    )

    assert proxy_resp.status_code == 401
