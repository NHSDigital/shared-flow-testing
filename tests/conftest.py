import pytest

from tests.utils.config import ENV

# FIXTURES FOR USE IN SET UP OF pytest_nhsd_apim
@pytest.fixture(scope="session")
def nhsd_apim_api_name():
    return ENV["api_name"]


@pytest.fixture(scope="session")
def nhsd_apim_proxy_name():
    return ENV["proxy_name"]