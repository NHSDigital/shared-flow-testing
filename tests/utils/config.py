# from .environment import ENV
from os import getenv


ENV = {
    "proxy_name": getenv("PROXY_NAME"),
    "api_name": getenv("API_NAME", "shared-flow-testing"),
    "source_commit_id": getenv("SOURCE_COMMIT_ID")
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
