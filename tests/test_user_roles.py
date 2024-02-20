import pytest
import requests


class TestUserRoles:
    """A test suite for testing userrole in id tokens/headers/userinfo"""

    @pytest.mark.parametrize(
        "additional_headers",
        [
            pytest.param(
                {},
                marks=pytest.mark.nhsd_apim_authorization(
                    access="healthcare_worker",
                    level="aal3",
                    login_form={"username": "656005750107"},
                    force_new_token=True,
                ),
                id="User role sent in id token",
            ),
            pytest.param(
                {},
                marks=pytest.mark.nhsd_apim_authorization(
                    access="healthcare_worker",
                    level="aal3",
                    login_form={"username": "787807429512"},
                    force_new_token=True,
                ),
                id="User role in user info - one role - (no header, not in id token)",
            ),
            pytest.param(
                {"NHSD-Session-URID": "656014452101"},
                marks=pytest.mark.nhsd_apim_authorization(
                    access="healthcare_worker",
                    level="aal3",
                    login_form={"username": "656005750104"},
                    force_new_token=True,
                ),
                id="User role sent in header (no in id token, multiple in user info)",
            ),
        ],
    )
    def test_user_role_happy_path(
        self, nhsd_apim_proxy_url, nhsd_apim_auth_headers, additional_headers
    ):
        resp = requests.get(
            url=f"{nhsd_apim_proxy_url}/user-role-service",
            headers={**nhsd_apim_auth_headers, **additional_headers},
        )

        assert resp.status_code == 200

    @pytest.mark.parametrize(
        "additional_headers,error_description",
        [
            pytest.param(
                {},
                "multiple roles found in user info, please check nhsd-session-urid",
                marks=pytest.mark.nhsd_apim_authorization(
                    access="healthcare_worker",
                    level="aal3",
                    login_form={"username": "656005750104"},
                    force_new_token=True,
                ),
                id="Multiple user roles found in userinfo",
            ),
            pytest.param(
                {},
                "no userroles available, please check nhsd-session-urid is valid",
                marks=pytest.mark.nhsd_apim_authorization(
                    access="healthcare_worker",
                    level="aal3",
                    login_form={"username": "Aal3"},
                    force_new_token=True,
                ),
                id="No user role provided by any means",
            ),
            pytest.param(
                {},
                "selected_roleid is misconfigured/invalid",
                marks=pytest.mark.nhsd_apim_authorization(
                    access="healthcare_worker",
                    level="aal3",
                    login_form={"username": "Aal4"},
                    force_new_token=True,
                ),
                id="User role sent in id token but empty",
            ),
            pytest.param(
                {},
                "nhsid_nrbac_roles is misconfigured/invalid",
                marks=pytest.mark.nhsd_apim_authorization(
                    access="healthcare_worker",
                    level="aal3",
                    login_form={"username": "Aal5"},
                    force_new_token=True,
                ),
                id="nrbac is malformed, or person_roleid is empty (in userinfo)",
            ),
            pytest.param(
                {"NHSD-Session-URID": "notAuserRole123"},
                "nhsd-session-urid is invalid",
                marks=pytest.mark.nhsd_apim_authorization(
                    access="healthcare_worker",
                    level="aal3",
                    login_form={"username": "656005750104"},
                    force_new_token=True,
                ),
                id="Invalid role in header",
            ),
        ],
    )
    def test_user_role_unhappy_path(
        self,
        nhsd_apim_proxy_url,
        nhsd_apim_auth_headers,
        additional_headers,
        error_description,
    ):
        resp = requests.get(
            url=f"{nhsd_apim_proxy_url}/user-role-service",
            headers={**nhsd_apim_auth_headers, **additional_headers},
        )

        assert resp.status_code == 400
        assert resp.json() == error_description

    @pytest.mark.parametrize(
        "additional_headers,error_description",
        [
            pytest.param(
                {},
                "selected_roleid is missing in your token",
                marks=pytest.mark.nhsd_apim_authorization(
                    access="patient",
                    level="P9",
                    login_form={"username": "9912003071"},
                    force_new_token=True,
                ),
                id="NHS Login combined: Role can't be used from token",
            ),
            pytest.param(
                {"NHSD-Session-URID": "9912003071"},
                "unable to retrieve user info",
                marks=pytest.mark.nhsd_apim_authorization(
                    access="patient",
                    level="P9",
                    login_form={"username": "9912003071"},
                    force_new_token=True,
                ),
                id="NHS Login combined: Can't use header to fetch from userinfo",
            ),
            pytest.param(
                {},
                "selected_roleid is missing in your token",
                marks=pytest.mark.nhsd_apim_authorization(
                    access="patient",
                    level="P9",
                    login_form={"username": "9912003071"},
                    authentication="separate",
                    force_new_token=True,
                ),
                id="NHS Login separate: Role can't be used from token",
            ),
            pytest.param(
                {"NHSD-Session-URID": "9912003071"},
                "unable to retrieve user info",
                marks=pytest.mark.nhsd_apim_authorization(
                    access="patient",
                    level="P9",
                    login_form={"username": "9912003071"},
                    authentication="separate",
                    force_new_token=True,
                ),
                id="NHS Login separate: Can't use header to fetch from userinfo",
            ),
            pytest.param(
                {},
                "selected_roleid is missing in your token",
                marks=pytest.mark.nhsd_apim_authorization(
                    access="healthcare_worker",
                    level="aal3",
                    login_form={"username": "656005750104"},
                    authentication="separate",
                    force_new_token=True,
                ),
                id="CIS2 separate: Role can't be used from token",
            ),
            pytest.param(
                {"NHSD-Session-URID": "656005750104"},
                "unable to retrieve user info",
                marks=pytest.mark.nhsd_apim_authorization(
                    access="healthcare_worker",
                    level="aal3",
                    login_form={"username": "656005750104"},
                    authentication="separate",
                    force_new_token=True,
                ),
                id="CIS2 separate: Can't use header to fetch from userinfo",
            ),
        ],
    )
    def test_error_when_not_cis2_combined_auth(
        self,
        nhsd_apim_proxy_url,
        nhsd_apim_auth_headers,
        additional_headers,
        error_description,
    ):
        resp = requests.get(
            url=f"{nhsd_apim_proxy_url}/user-role-service",
            headers={**nhsd_apim_auth_headers, **additional_headers},
        )

        assert resp.status_code == 400
        assert resp.json() == error_description
