# from .environment import ENV
from os import getenv


ENV = {
    "proxy_name": getenv("PROXY_NAME"),
    "api_name": getenv("API_NAME", "shared-flow-testing"),
    "source_commit_id": getenv("SOURCE_COMMIT_ID"),
    "oauth_base_uri": getenv("OAUTH_BASE_URI"),
    "access_token_hash_secret": getenv("ACCESS_TOKEN_HASH_SECRET"),
}

# OLD CONFIG
# # Api Details
# ENVIRONMENT = ENV["environment"]
# BASE_URL = f"https://{ENVIRONMENT}.api.service.nhs.uk"
# BASE_PATH = ENV["base_path"]

# # Jwt variables
# JWT_PRIVATE_KEY_ABSOLUTE_PATH = ENV["jwt_private_key_absolute_path"]
# ID_TOKEN_NHS_LOGIN_PRIVATE_KEY_ABSOLUTE_PATH = ENV["id_token_nhs_login_private_key_absolute_path"]
# ID_TOKEN_PRIVATE_KEY_ABSOLUTE_PATH = ENV["id_token_private_key_absolute_path"]
# SERVICE_BASE_PATH = ENV['service_base_path']
# SERVICE_NAME = ENV['service_name']
# ACCESS_TOKEN_HASH_SECRET = environ.get("ACCESS_TOKEN_HASH_SECRET")
# APP_CLIENT_ID = environ.get("APP_CLIENT_ID")
# OAUTH_PROXY = environ.get("OAUTH_PROXY")


{
    "messageID": "rrt-1913326728553154966-c-geu2-23780-1783839-1",
    "client": {
        "ip": "86.135.86.49",
        "received_start": "1678207864981",
        "received_end": "1678207864981",
        "sent_start": "1678207864984",
        "sent_end": "1678207864985",
        "user_agent": "python-requests/2.27.1",
    },
    "request": {
        "uri": "/shared-flow-testing-pr-83/splunk-test",
        "verb": "GET",
        "content_type": "",
        "content_length": "0",
        "content_encoding": "",
        "requestID": "",
        "correlationID": "",
        "host": "internal-dev.api.service.nhs.uk",
        "port": "443",
        "uri_path": "/shared-flow-testing-pr-83/splunk-test",
        "uri_params": "",
    },
    "meta": {
        "ASID": "",
        "api_guid": "3bf28d91-7109-4387-bf1a-e26f673eb0e8",
        "api_spec_guid": "fc17b6fe-c3c7-4801-8331-3f87c9f26e62",
        "application": "unknown",
        "application_id": "",
        "application_name": "",
        "client_id": "",
        "env": "internal-dev",
        "organization": "nhsd-nonprod",
        "product": "",
    },
    "proxy": {
        "name": "shared-flow-testing-pr-83",
        "revision": "7",
        "basepath": "shared-flow-testing-pr-83",
        "suffix": "/splunk-test",
    },
    "auth": {
        "access_token_hash": "",
        "user": {"user_id": ""},
        "meta": {
            "auth_type": "app",
            "grant_type": "",
            "level": "-",
            "provider": "apim",
        },
        "id_token_acr": "",
        "grant_type": "",
        "authorization": "",
        "id_token_subject": "",
        "id_token_issuer": "",
        "scope": "",
    },
    "target": {
        "host": "",
        "status_code": "",
        "content_length": "",
        "received_start": "",
        "received_end": "",
        "sent_start": "",
        "sent_end": "",
        "port": "",
    },
    "error": {
        "is_error": "true",
        "is_policy_error": "1",
        "is_target_error": "0",
        "policy_error_policy_name": "OauthV2.VerifyAccessToken",
        "policy_error_flow_name": "SplunkTestEndpoint",
        "error": "com.apigee.flow.message.MessageImpl@329f61",
        "content": '\n    {\n        "resourceType": "OperationOutcome",\n        "issue": [\n            {\n            "severity": "error",\n            "code": "401",\n            "details": {\n                "coding": [\n                {\n                    "code": "401",\n                    "display": "Unauthorized"\n                }\n                ]\n            },\n            "diagnostics": "{"fault":{"faultstring":"Invalid access token","detail":{"errorcode":"oauth.v2.InvalidAccessToken"}}}"\n            }\n        ]\n    }\n    ',
        "message": "Invalid access token",
        "status_code": "401",
        "reason_phrase": "Unauthorized",
        "transport_message": "com.apigee.messaging.adaptors.http.message.HttpResponseMessage@3d8b6e44",
        "state": "PROXY_REQ_FLOW",
    },
    "response": {
        "status_code": "",
        "content_type": "",
        "content_length": "",
        "content_encoding": "",
        "content_body": "",
    },
}
