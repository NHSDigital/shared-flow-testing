from .environment import ENV

# Api Details
ENVIRONMENT = ENV["environment"]
BASE_URL = f"https://{ENVIRONMENT}.api.service.nhs.uk"
BASE_PATH = ENV["base_path"]

# Jwt variables
JWT_PRIVATE_KEY_ABSOLUTE_PATH = ENV["jwt_private_key_absolute_path"]
ID_TOKEN_NHS_LOGIN_PRIVATE_KEY_ABSOLUTE_PATH = ENV["id_token_nhs_login_private_key_absolute_path"]
ID_TOKEN_PRIVATE_KEY_ABSOLUTE_PATH = ENV["id_token_private_key_absolute_path"]
SERVICE_BASE_PATH = ENV['service_base_path']
