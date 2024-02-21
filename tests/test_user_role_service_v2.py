import pytest
import requests


def set_custom_header_name(headers):
    default_header = headers.get("NHSD-Session-URID")
    return {"NHSD-URID": default_header}


class TestUserRoles:
    """A test suite for testing userrole in id tokens/headers/userinfo"""

    happy_path_params = [
        pytest.param(
            {},
            "555254242105",
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
            "555254242105",
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
            "656014452101",
            marks=pytest.mark.nhsd_apim_authorization(
                access="healthcare_worker",
                level="aal3",
                login_form={"username": "656005750104"},
                force_new_token=True,
            ),
            id="User role sent in header (no in id token, multiple in user info)",
        ),
    ]
    unhappy_path_params = [
        pytest.param(
            {},
            "multiple roles found in user info, please check NHSD-Session-URID",
            401,
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
            "no userroles available, please check NHSD-Session-URID is valid",
            401,
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
            401,
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
            401,
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
            "NHSD-Session-URID is invalid",
            401,
            marks=pytest.mark.nhsd_apim_authorization(
                access="healthcare_worker",
                level="aal3",
                login_form={"username": "656005750104"},
                force_new_token=True,
            ),
            id="Invalid role in header",
        ),
    ]
    when_not_cis2_params = [
        pytest.param(
            {},
            "selected_roleid is missing in your token",
            401,
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
            500,
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
            401,
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
            500,
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
            401,
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
            500,
            marks=pytest.mark.nhsd_apim_authorization(
                access="healthcare_worker",
                level="aal3",
                login_form={"username": "656005750104"},
                authentication="separate",
                force_new_token=True,
            ),
            id="CIS2 separate: Can't use header to fetch from userinfo",
        ),
    ]

    @pytest.mark.parametrize("additional_headers,expected_urid", happy_path_params)
    def test_user_role_happy_path_default_header(
        self,
        nhsd_apim_proxy_url,
        nhsd_apim_auth_headers,
        additional_headers,
        expected_urid,
    ):
        resp = requests.get(
            url=f"{nhsd_apim_proxy_url}/user-role-service-v2-default-header",
            headers={**nhsd_apim_auth_headers, **additional_headers},
        )

        print(resp.json())

        assert resp.status_code == 200
        assert resp.headers["NHSD-Session-URID"] == expected_urid

    @pytest.mark.parametrize("additional_headers,expected_urid", happy_path_params)
    def test_user_role_happy_path_custom_header(
        self,
        nhsd_apim_proxy_url,
        nhsd_apim_auth_headers,
        additional_headers,
        expected_urid,
    ):
        # Swap the header names if not done already
        additional_headers = set_custom_header_name(additional_headers)

        resp = requests.get(
            url=f"{nhsd_apim_proxy_url}/user-role-service-v2-custom-header",
            headers={**nhsd_apim_auth_headers, **additional_headers},
        )

        assert resp.status_code == 200
        assert resp.headers["NHSD-URID"] == expected_urid

    @pytest.mark.parametrize(
        "additional_headers,error_description,status_code", unhappy_path_params
    )
    def test_user_role_unhappy_path_default_header(
        self,
        nhsd_apim_proxy_url,
        nhsd_apim_auth_headers,
        additional_headers,
        error_description,
        status_code,
    ):
        resp = requests.get(
            url=f"{nhsd_apim_proxy_url}/user-role-service-v2-default-header",
            headers={**nhsd_apim_auth_headers, **additional_headers},
        )

        assert resp.status_code == status_code
        assert resp.json()["issue"][0]["diagnostics"] == error_description

    @pytest.mark.parametrize(
        "additional_headers,error_description,status_code", unhappy_path_params
    )
    def test_user_role_unhappy_path_custom_header(
        self,
        nhsd_apim_proxy_url,
        nhsd_apim_auth_headers,
        additional_headers,
        error_description,
        status_code,
    ):
        # Swap the header names if not done already
        additional_headers = set_custom_header_name(additional_headers)
        error_description = error_description.replace("NHSD-Session-URID", "NHSD-URID")

        resp = requests.get(
            url=f"{nhsd_apim_proxy_url}/user-role-service-v2-custom-header",
            headers={**nhsd_apim_auth_headers, **additional_headers},
        )

        assert resp.status_code == status_code
        assert resp.json()["issue"][0]["diagnostics"] == error_description

    @pytest.mark.parametrize(
        "additional_headers,error_description,status_code", when_not_cis2_params
    )
    def test_error_when_not_cis2_combined_auth_default_header(
        self,
        nhsd_apim_proxy_url,
        nhsd_apim_auth_headers,
        additional_headers,
        error_description,
        status_code,
    ):
        resp = requests.get(
            url=f"{nhsd_apim_proxy_url}/user-role-service-v2-default-header",
            headers={**nhsd_apim_auth_headers, **additional_headers},
        )

        assert resp.status_code == status_code
        assert resp.json()["issue"][0]["diagnostics"] == error_description

    @pytest.mark.parametrize(
        "additional_headers,error_description,status_code", when_not_cis2_params
    )
    def test_error_when_not_cis2_combined_auth_custom_header(
        self,
        nhsd_apim_proxy_url,
        nhsd_apim_auth_headers,
        additional_headers,
        error_description,
        status_code,
    ):
        # Swap the header names if not done already
        additional_headers = set_custom_header_name(additional_headers)

        resp = requests.get(
            url=f"{nhsd_apim_proxy_url}/user-role-service-v2-custom-header",
            headers={**nhsd_apim_auth_headers, **additional_headers},
        )

        assert resp.status_code == status_code
        assert resp.json()["issue"][0]["diagnostics"] == error_description
