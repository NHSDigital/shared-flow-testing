# flake8: noqa
from time import time

import pytest
from api_test_utils.api_test_session_config import APITestSessionConfig
from api_test_utils.apigee_api_apps import ApigeeApiDeveloperApps
from api_test_utils.apigee_api_products import ApigeeApiProducts
from api_test_utils.apigee_api_trace import ApigeeApiTraceDebug
from api_test_utils.oauth_helper import OauthHelper

from .configuration import config

pytest_plugins = [
   "api_test_utils.fixtures",
]

@pytest.fixture(scope='session')
def api_test_config() -> APITestSessionConfig:
    """
        this imports a 'standard' test session config,
        which builds the proxy uri

    """
    return APITestSessionConfig()


@pytest.fixture()
def app():
    """
    Import the test utils module to be able to:
        - Create apigee test application
            - Update custom attributes
            - Update custom ratelimits
            - Update products to the test application
    """
    return ApigeeApiDeveloperApps()


@pytest.fixture()
def product():
    """
    Import the test utils module to be able to:
        - Create apigee test product
            - Update custom scopes
            - Update environments
            - Update product paths
            - Update custom attributes
            - Update proxies to the product
            - Update custom ratelimits
    """
    return ApigeeApiProducts()


@pytest.fixture()
def debug():
    """
    Import the test utils module to be able to:
        - Use the trace tool and get context variables after making a request to Apigee
    """
    return ApigeeApiTraceDebug(proxy=config.SERVICE_NAME)


@pytest.fixture()
async def test_app_and_product(app, product):
    """Create a test app and product which can be modified in the test"""
    await product.create_new_product()

    await app.create_new_app()

    await product.update_proxies([f"identity-service-mock-internal-dev", "shared-flow-testing-internal-dev"])

    app.oauth = OauthHelper(app.client_id, app.client_secret, app.callback_url)

    await product.update_scopes(
        [
            "urn:nhsd:apim:app:level3:shared-flow-testing",
            "urn:nhsd:apim:user-nhs-id:aal3:shared-flow-testing",
            "urn:nhsd:apim:user-nhs-login:P9:shared-flow-testing",
        ]
    )
    await app.add_api_product([product.name])
    await app.set_custom_attributes(
        {
            "jwks-resource-url": "https://raw.githubusercontent.com/NHSDigital/"
                                 "identity-service-jwks/main/jwks/internal-dev/"
                                 "9baed6f4-1361-4a8e-8531-1f8426e3aba8.json"
        }
    )

    yield product, app

    await app.destroy_app()
    await product.destroy_product()


@pytest.fixture()
async def get_token(test_app_and_product):
    """Call identity server to get an access token"""
    test_product, test_app = test_app_and_product
    oauth = OauthHelper(
        client_id=test_app.client_id,
        client_secret=test_app.client_secret,
        redirect_uri=test_app.callback_url,
    )
    token_resp = await oauth.get_token_response(grant_type="authorization_code")
    assert token_resp["status_code"] == 200
    return token_resp["body"]


@pytest.fixture()
async def get_token_client_credentials(test_app_and_product):
    """Call identity server to get an access token"""
    test_product, test_app = test_app_and_product
    oauth = OauthHelper(
        client_id=test_app.client_id,
        client_secret=test_app.client_secret,
        redirect_uri=test_app.callback_url,
    )
    jwt = oauth.create_jwt(kid="test-1")
    token_resp = await oauth.get_token_response(
        grant_type="client_credentials", _jwt=jwt
    )
    assert token_resp["status_code"] == 200
    return token_resp["body"]


@pytest.fixture()
async def get_token_cis2_token_exchange(test_app_and_product):
    """Call identity server to get an access token"""
    test_product, test_app = test_app_and_product
    oauth = OauthHelper(
        client_id=test_app.client_id,
        client_secret=test_app.client_secret,
        redirect_uri=test_app.callback_url,
    )

    claims = {
        'at_hash': 'tf_-lqpq36lwO7WmSBIJ6Q',
        'sub': 'lala',
        'auditTrackingId': '91f694e6-3749-42fd-90b0-c3134b0d98f6-1546391',
        'amr': ['N3_SMARTCARD'],
        'iss': 'https://am.nhsint.auth-ptl.cis2.spineservices.nhs.uk:443/'
               'openam/oauth2/realms/root/realms/NHSIdentity/realms/Healthcare',
        'tokenName': 'id_token',
        'aud': '969567331415.apps.national',
        'c_hash': 'bc7zzGkClC3MEiFQ3YhPKg',
        'acr': 'AAL3_ANY',
        'org.forgerock.openidconnect.ops': '-I45NjmMDdMa-aNF2sr9hC7qEGQ',
        's_hash': 'LPJNul-wow4m6Dsqxbning',
        'azp': '969567331415.apps.national',
        'auth_time': 1610559802,
        'realm': '/NHSIdentity/Healthcare',
        'exp': int(time()) + 6000,
        'tokenType': 'JWTToken',
        'iat': int(time()) - 100
    }

    with open(config.ID_TOKEN_PRIVATE_KEY_ABSOLUTE_PATH, "r") as f:
        contents = f.read()

    client_assertion_jwt = oauth.create_jwt(kid="test-1")
    id_token_jwt = oauth.create_id_token_jwt(kid="identity-service-tests-1", claims=claims, signing_key=contents)

    # When
    token_resp = await oauth.get_token_response(
        grant_type="token_exchange",
        data={
            "grant_type": "urn:ietf:params:oauth:grant-type:token-exchange",
            "subject_token_type": "urn:ietf:params:oauth:token-type:id_token",
            "client_assertion_type": "urn:ietf:params:oauth:client-assertion-type:jwt-bearer",
            "subject_token": id_token_jwt,
            "client_assertion": client_assertion_jwt,
        },
    )
    assert token_resp["status_code"] == 200
    return token_resp["body"]


@pytest.fixture()
async def get_token_nhs_login_token_exchange(test_app_and_product):
    """Call identity server to get an access token"""
    test_product, test_app = test_app_and_product
    oauth = OauthHelper(
        client_id=test_app.client_id,
        client_secret=test_app.client_secret,
        redirect_uri=test_app.callback_url,
    )

    id_token_claims = {
        "aud": "tf_-APIM-1",
        "id_status": "verified",
        "token_use": "id",
        "auth_time": 1616600683,
        "iss": "https://internal-dev.api.service.nhs.uk",
        "vot": "P9.Cp.Cd",
        "exp": int(time()) + 600,
        "iat": int(time()) - 10,
        "nhs_number": "900000000001",
        "vtm": "https://auth.sandpit.signin.nhs.uk/trustmark/auth.sandpit.signin.nhs.uk",
        "jti": "b68ddb28-e440-443d-8725-dfe0da330118",
        "identity_proofing_level": "P9",
    }
    id_token_headers = {
        "sub": "49f470a1-cc52-49b7-beba-0f9cec937c46",
        "aud": "APIM-1",
        "kid": "nhs-login",
        "iss": "https://internal-dev.api.service.nhs.uk",
        "typ": "JWT",
        "exp": 1616604574,
        "iat": 1616600974,
        "alg": "RS512",
        "jti": "b68ddb28-e440-443d-8725-dfe0da330118",
    }
    with open(config.ID_TOKEN_NHS_LOGIN_PRIVATE_KEY_ABSOLUTE_PATH, "r") as f:
        contents = f.read()

    client_assertion_jwt = oauth.create_jwt(kid="test-1")
    id_token_jwt = oauth.create_id_token_jwt(
        algorithm="RS512",
        claims=id_token_claims,
        headers=id_token_headers,
        signing_key=contents,
    )

    # When
    token_resp = await oauth.get_token_response(
        grant_type="token_exchange",
        data={
            "grant_type": "urn:ietf:params:oauth:grant-type:token-exchange",
            "subject_token_type": "urn:ietf:params:oauth:token-type:id_token",
            "client_assertion_type": "urn:ietf:params:oauth:client-assertion-type:jwt-bearer",
            "subject_token": id_token_jwt,
            "client_assertion": client_assertion_jwt,
        },
    )
    assert token_resp["status_code"] == 200
    return token_resp["body"]
