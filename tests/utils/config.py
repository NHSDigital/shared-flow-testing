from os import getenv


ENV = {
    "proxy_name": getenv("PROXY_NAME"),
    "api_name": getenv("API_NAME", "shared-flow-testing"),
    "source_commit_id": getenv("SOURCE_COMMIT_ID"),
    "oauth_base_uri": getenv("OAUTH_BASE_URI"),
    "access_token_hash_secret": getenv("ACCESS_TOKEN_HASH_SECRET"),
}
