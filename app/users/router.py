# Router describes internal logic for working on each user URL
# request that starts with a certain prefix
from typing import Annotated
from fastapi import (
    APIRouter,
    HTTPException,
    status,
    Form,
    Depends
)
from app.users.dao import UserDAO
from app.users.schemas import SUser
from app.users.models import User
from app.users.auth import (
    get_password_hash,
    authenticate_user,
)
from app.users.jwt.token_info import TokenInfo
from app.users.jwt.create import (
    create_access_token,
    create_refresh_token
)
from app.users.jwt.current_user import (
    get_current_user_from_refresh,
    get_current_user_from_access
)

router = APIRouter(prefix="/user", tags=["Authorization and registration"])


# TODO Maybe allow only certain characters in the password and nickname
@router.post("/register/", summary="Register a new user")
async def register_user(user_data: Annotated[SUser, Form()]) -> dict:
    user = await UserDAO.find_one_or_none(nickname=user_data.nickname)
    if user is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"The user '{user_data.nickname}' already exists")
    user_dict = {"nickname": user_data.nickname,
                 "password": user_data.password}
    user_dict["password"] = get_password_hash(user_data.password)
    await UserDAO.add(**user_dict)
    return {"message": "You have registered successfully!"}


@router.post("/login/",
             response_model=TokenInfo,
             summary="Login to an existing account")
def authorize_user(user: Annotated[User, Depends(authenticate_user)]
                   ) -> TokenInfo:
    access_token = create_access_token(user)
    refresh_token = create_refresh_token(user)
    return TokenInfo(access_token=access_token, refresh_token=refresh_token)


@router.post("/me/jwt/refresh_access_token/",
             summary="Refresh access token using refresh token",
             response_model=TokenInfo,
             response_model_exclude_none=True)
def auth_refresh_jwt(user_data: SUser =
                     Depends(get_current_user_from_refresh)):
    access_token = create_access_token(user_data)
    return TokenInfo(access_token=access_token)


@router.get("/me/", summary="Get current user data")
def auth_user_check_self_info(user_data: SUser =
                              Depends(get_current_user_from_access)) -> dict:
    return {"nickname": user_data.nickname}
