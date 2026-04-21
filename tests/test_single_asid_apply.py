import pytest
import requests
import jwt

from uuid import uuid4
from time import time

from tests.utils.config import ENV
from tests.utils.helpers import get_variable_from_trace


class TestSingleAsidApply:
    """Test Single Asid Apply are available"""
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
    

