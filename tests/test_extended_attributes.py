import pytest
import requests
import jwt

from uuid import uuid4
from time import time

from tests.utils.config import ENV
from tests.utils.helpers import get_variable_from_trace


class TestExtendedAttributes:
    """Test extended attributes are available"""

    def get_token_client_credentials(self, client_id, private_key):
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

    @pytest.mark.parametrize(
        "new_attribute,flow_vars_to_check",
        [
            pytest.param(
                {
                    "name": "apim-app-flow-vars",
                    "value": '{"proxy":{"allowed":{"update":true}}}',
                },
                [{"name": "apim-app-flow-vars.proxy.allowed.update", "value": "true"}],
                id="Single attribute",
            ),
            pytest.param(
                {
                    "name": "apim-app-flow-vars",
                    "value": '{"attr_a": "value_a", "attr_b": "value_b"}',
                },
                [
                    {
                        "name": "apim-app-flow-vars.attr_a",
                        "value": "value_a"
                    },
                    {
                        "name": "apim-app-flow-vars.attr_b",
                        "value": "value_b"
                    }
                ],
                id="Multiple attributes",
            ),
        ],
    )
    def test_extended_attributes(
        self,
        nhsd_apim_proxy_url,
        _create_function_scoped_test_app,
        _proxy_product_with_scope,
        _jwt_keys,
        developer_apps_api,
        nhsd_apim_config,
        trace,
        new_attribute,
        flow_vars_to_check
    ):
        # Update test app with proxy product and the extended attribute
        app = _create_function_scoped_test_app
        app["apiProducts"] = [_proxy_product_with_scope["name"]]
        app["attributes"].append(new_attribute)
        app = developer_apps_api.put_app_by_name(
            email=nhsd_apim_config["APIGEE_DEVELOPER"], app_name=app["name"], body=app
        )

        # Trace call to shared flow proxy extended attributes endpoint
        session_name = str(uuid4())
        header_filters = {"trace_id": session_name}
        trace.post_debugsession(session=session_name, header_filters=header_filters)

        access_token = self.get_token_client_credentials(
            client_id=app["credentials"][0]["consumerKey"],
            private_key=_jwt_keys["private_key_pem"],
        )
        proxy_resp = requests.get(
            url=f"{nhsd_apim_proxy_url}/extended-attributes",
            headers={"Authorization": f"Bearer {access_token}", **header_filters},
        )
        assert proxy_resp.status_code == 200

        # Extract variables from trace and assert
        extended_attributes = get_variable_from_trace(
            trace, session_name, "app." + new_attribute["name"]
        )
        assert extended_attributes == new_attribute["value"]

        for flow_var in flow_vars_to_check:
            assert flow_var["value"] == get_variable_from_trace(
            trace, session_name, flow_var["name"]
        )

        trace.delete_debugsession_by_name(session_name)

    @pytest.mark.nhsd_apim_authorization(access="application", level="level3")
    def test_no_attribute(
        self,
        nhsd_apim_proxy_url,
        nhsd_apim_auth_headers,
        trace,
    ):
        # Trace call to shared flow proxy extended attributes endpoint
        session_name = str(uuid4())
        header_filters = {"trace_id": session_name}
        trace.post_debugsession(session=session_name, header_filters=header_filters)

        proxy_resp = requests.get(
            url=f"{nhsd_apim_proxy_url}/extended-attributes",
            headers={**nhsd_apim_auth_headers, **header_filters},
        )
        assert proxy_resp.status_code == 200

        # Extract variable from trace and assert
        extended_attributes = get_variable_from_trace(
            trace, session_name, "app.apim-app-flow-vars"
        )

        trace.delete_debugsession_by_name(session_name)

        assert not extended_attributes

    def test_invalid_json(
        self,
        nhsd_apim_proxy_url,
        _create_function_scoped_test_app,
        _proxy_product_with_scope,
        _jwt_keys,
        developer_apps_api,
        nhsd_apim_config,
        trace,
    ):
        new_attribute = {
            "name": "apim-app-flow-vars",
            "value": '{"proxy":{{"allowed":{"update":true}}}',
        }

        # Update test app with proxy product and the extended attribute
        app = _create_function_scoped_test_app
        app["apiProducts"] = [_proxy_product_with_scope["name"]]
        app["attributes"].append(new_attribute)
        app = developer_apps_api.put_app_by_name(
            email=nhsd_apim_config["APIGEE_DEVELOPER"], app_name=app["name"], body=app
        )

        # Trace call to shared flow proxy extended attributes endpoint
        session_name = str(uuid4())
        header_filters = {"trace_id": session_name}
        trace.post_debugsession(session=session_name, header_filters=header_filters)

        access_token = self.get_token_client_credentials(
            client_id=app["credentials"][0]["consumerKey"],
            private_key=_jwt_keys["private_key_pem"],
        )
        proxy_resp = requests.get(
            url=f"{nhsd_apim_proxy_url}/extended-attributes",
            headers={"Authorization": f"Bearer {access_token}", **header_filters},
        )
        assert proxy_resp.status_code == 500

        # Var is None unless the InvalidJson RaiseFault error has been thrown
        raise_fault_var = get_variable_from_trace(
            trace, session_name, "raisefault.RaiseFault.InvalidJson"
        )

        trace.delete_debugsession_by_name(session_name)

        assert raise_fault_var is not None
