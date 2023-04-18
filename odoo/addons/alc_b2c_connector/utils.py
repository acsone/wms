from fastapi.security import APIKeyHeader

api_key_header = APIKeyHeader(
    name="api-key",
    description="In this demo, you can use a user's login as api key.",
)
