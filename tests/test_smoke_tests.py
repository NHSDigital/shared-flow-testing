import requests
import pytest
from tests.utils.config import ENV


class TestHealthEndpoints:
    """Test ping and status endpoints to check health"""

    @pytest.mark.smoketest
    def test_ping(nhsd_apim_proxy_url):
        resp = requests.get(f"{nhsd_apim_proxy_url}/_ping")
        assert resp.status_code == 200

    @pytest.mark.smoketest
    def test_wait_for_ping(nhsd_apim_proxy_url):
        retries = 0
        resp = requests.get(f"{nhsd_apim_proxy_url}/_ping")
        deployed_commitId = resp.json().get("commitId")

        while (
            deployed_commitId != ENV["source_commit_id"]
            and retries <= 30
            and resp.status_code == 200
        ):
            resp = requests.get(f"{nhsd_apim_proxy_url}/_ping")
            deployed_commitId = resp.json().get("commitId")
            retries += 1

        if resp.status_code != 200:
            pytest.fail(f"Status code {resp.status_code}, expecting 200")
        elif retries >= 30:
            pytest.fail("Timeout Error - max retries")

        assert deployed_commitId == ENV["source_commit_id"]

    @pytest.mark.smoketest
    def test_status(nhsd_apim_proxy_url, status_endpoint_auth_headers):
        resp = requests.get(
            f"{nhsd_apim_proxy_url}/_status", headers=status_endpoint_auth_headers
        )
        assert resp.status_code == 200
        body = resp.json()

        assert body["status"] == "pass"
        assert sorted(body.keys()) == sorted(
            ["status", "version", "revision", "releaseId", "commitId", "checks"]
        )
        assert body["checks"]["healthcheck"]["status"] == "pass"
        assert body["checks"]["healthcheck"]["responseCode"] == 200
        assert body["checks"]["healthcheck"]["outcome"] == "Hello, Guest!"

    @pytest.mark.smoketest
    def test_wait_for_status(nhsd_apim_proxy_url, status_endpoint_auth_headers):
        retries = 0
        resp = requests.get(
            f"{nhsd_apim_proxy_url}/_status", headers=status_endpoint_auth_headers
        )
        deployed_commitId = resp.json().get("commitId")

        while (
            deployed_commitId != ENV["source_commit_id"]
            and retries <= 30
            and resp.status_code == 200
            and resp.json().get("version")
        ):
            resp = requests.get(
                f"{nhsd_apim_proxy_url}/_status", headers=status_endpoint_auth_headers
            )
            deployed_commitId = resp.json().get("commitId")
            retries += 1

        if resp.status_code != 200:
            pytest.fail(f"Status code {resp.status_code}, expecting 200")
        elif retries >= 30:
            pytest.fail("Timeout Error - max retries")
        elif not resp.json().get("version"):
            pytest.fail("version not found")

        assert deployed_commitId == ENV["source_commit_id"]
