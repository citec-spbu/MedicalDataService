import jwt
from app.config import jwt_settings
from datetime import (
    timedelta,
    datetime
)


def encode_jwt(payload: dict,
               private_key: str = jwt_settings.private_key,
               algorithm: str = jwt_settings.algorithm,
               expire_minutes: int = jwt_settings.access_token_expire_minutes,
               expire_timedelta: timedelta | None = None
               ) -> str:
    """
    Encode jwt token using private_key
    :param payload: payload of jwt token
    :param private_key: encryption key
    :param algorithm: encryption algorithm
    :param expire_minutes: token lifetime in minutes
    :param expire_timedelta: token lifetime im timedelta
    :return: Encoded JWT
    """
    to_encode = payload.copy()
    now = datetime.utcnow()
    if expire_timedelta is not None:
        expire = now + expire_timedelta
    else:
        expire = now + timedelta(minutes=expire_minutes)
    to_encode.update(exp=expire,
                     iat=now)
    encoded = jwt.encode(to_encode,
                         private_key,
                         algorithm=jwt_settings.algorithm)
    return encoded


def decoded_jwt(token: str,
                public_key: str = jwt_settings.public_key,
                algorithm: str = jwt_settings.algorithm
                ) -> dict:
    """
    Get payload of current jwt token
    Throws InvalidTokenError if token is out of date
    :param token: jwt token string
    :param public_key: decryption key
    :param algorithm: encryption algorithm
    :return: payload of jwt
    """
    decoded = jwt.decode(token, public_key, algorithms=[algorithm])
    return decoded
