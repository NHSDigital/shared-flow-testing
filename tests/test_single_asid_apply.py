import pytest
import requests
import jwt

from uuid import uuid4
from time import time

from tests.utils.config import ENV
from tests.utils.helpers import get_variable_from_trace


class TestSingleAsidApply:
    """Test Single Asid Apply are available"""

    @staticmethod
    def _get_token_client_credentials(client_id, private_key):
        claims = {
            "sub": client_id,
            "iss": client_id,
            "jti": str(uuid4()),
            "aud": ENV["oauth_base_uri"] + "/token",
            "exp": int(time()) + 300,  # 5 minutes in the future
        }

        client_assertion = jwt.encode(
            claims, private_key, algorithm="RS512", headers={"kid": "test-1"}
        )
        token_data = {
            "client_assertion_type": "urn:ietf:params:oauth:client-assertion-type:jwt-bearer",
            "client_assertion": client_assertion,
            "grant_type": "client_credentials",
        }

        token_resp = requests.post(
            ENV["oauth_base_uri"] + "/token",
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            data=token_data,
        )

        assert token_resp.status_code == 200

        return token_resp.json()["access_token"]
    @pytest.mark.parametrize("expected_status_code, expected_message", [(400, "no_headers")])
    def test_no_header_present(
        self,
        nhsd_apim_proxy_url,
        expected_status_code,
        expected_message
    ):
        # Create test app and don't define any apiProducts

        proxy_resp = requests.get(
            url=f"{nhsd_apim_proxy_url}/single-asid",
            timeout=60
        )

        assert proxy_resp.status_code == expected_status_code
        assert proxy_resp.json().get("error") == expected_message
    

