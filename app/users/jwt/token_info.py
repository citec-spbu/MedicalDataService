from pydantic import BaseModel


class TokenInfo(BaseModel):
    access_token: str
    token_type: str = "Bearer"


TOKEN_TYPE_FILED = "type"
ACCESS_TOKEN_TYPE = "access"
REFRESH_TOKEN_TYPE = "refresh"
