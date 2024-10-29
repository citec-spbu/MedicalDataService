from jwt.exceptions import InvalidTokenError
from fastapi import (
    HTTPException,
    status,
    Depends
)
from fastapi.security import OAuth2PasswordBearer
from app.users.dao import UserDAO
from app.users.schemas import SUser
from app.users.jwt.conversion import decoded_jwt
from app.users.jwt.token_info import (
    TOKEN_TYPE_FILED,
    ACCESS_TOKEN_TYPE,
    REFRESH_TOKEN_TYPE
)


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/user/login/get_token/")


def get_current_token_payload(token: str = Depends(oauth2_scheme)) -> dict:
    try:
        payload = decoded_jwt(token=token)
    except InvalidTokenError as err:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail=f"Invalid token error: {err}",
                            headers={"WWW-Authenticate": "Bearer"})
    return payload


def validate_token_type(payload: dict, token_type: str) -> bool:
    current_token_type = payload.get(TOKEN_TYPE_FILED)
    if current_token_type != token_type:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail=f"Invalid token type: {
                                current_token_type!r}, "
                            f"expected: {token_type!r}",
                            headers={"WWW-Authenticate": "Bearer"})
    return True


async def get_user_by_token_sub(payload: dict) -> SUser:
    nickname: str = payload.get("sub")
    user = await UserDAO.find_one_or_none(nickname=nickname)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token (user not found)",
            headers={"WWW-Authenticate": "Bearer"})
    return user


async def get_current_user_from_access(payload: dict =
                                       Depends(get_current_token_payload)
                                       ) -> SUser:
    validate_token_type(payload, ACCESS_TOKEN_TYPE)
    return await get_user_by_token_sub(payload)


async def get_current_user_from_refresh(payload: dict =
                                        Depends(get_current_token_payload)
                                        ) -> SUser:
    validate_token_type(payload, REFRESH_TOKEN_TYPE)
    return await get_user_by_token_sub(payload)
