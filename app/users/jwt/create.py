from datetime import timedelta
from app.config import jwt_settings
from app.users.models import User
from app.users.jwt.conversion import encode_jwt
from app.users.jwt.token_info import (
    TOKEN_TYPE_FILED,
    ACCESS_TOKEN_TYPE,
    REFRESH_TOKEN_TYPE
)


def create_jwt(token_type: str,
               token_data: dict,
               expire_minutes: int = jwt_settings.access_token_expire_minutes,
               expire_timedelta: timedelta | None = None
               ) -> str:
    jwt_payload = {TOKEN_TYPE_FILED: token_type}
    jwt_payload.update(token_data)
    return encode_jwt(payload=jwt_payload,
                      expire_minutes=expire_minutes,
                      expire_timedelta=expire_timedelta)


def create_access_token(user: User) -> str:
    jwt_payload = {
        "sub": user.nickname,
        "role": user.role.name
    }
    return create_jwt(token_type=ACCESS_TOKEN_TYPE,
                      token_data=jwt_payload,
                      expire_minutes=jwt_settings.access_token_expire_minutes)


def create_refresh_token(user: User) -> str:
    jwt_payload = {
        "sub": user.nickname,
        "role": user.role.name
    }
    return create_jwt(token_type=REFRESH_TOKEN_TYPE,
                      token_data=jwt_payload,
                      expire_timedelta=timedelta(
                          days=jwt_settings.refresh_token_exprire_days))
