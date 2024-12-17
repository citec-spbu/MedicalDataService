# Router describes internal logic for working on each user URL
# request that starts with a certain prefix
from typing import Annotated
from fastapi import (
    APIRouter,
    HTTPException,
    status,
    Form,
    Depends,
    Response,
    Cookie
)
from app.users.dao import UserDAO
from app.users.schemas import SUser, SUserWithRole
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
    get_current_user_from_access,
    get_current_user_with_role_from_access,
    validate_token_type,
    get_user_by_token_sub
)
from typing import Optional
from app.users.jwt.conversion import decoded_jwt
from app.users.jwt.token_info import (
    TOKEN_TYPE_FILED,
    ACCESS_TOKEN_TYPE,
    REFRESH_TOKEN_TYPE
)

router = APIRouter(prefix="/user", tags=["Authorization and registration"])

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
def authorize_user(
        response: Response,
        user: Annotated[User, Depends(authenticate_user)]
) -> TokenInfo:
    access_token = create_access_token(user)
    refresh_token = create_refresh_token(user)

    # refresh token в httpOnly cookie
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=False,  # для HTTPS
        samesite="lax",
        max_age=60 * 60 * 24 * 30  # 30 дней
    )

    return TokenInfo(access_token=access_token)


@router.post("/refresh",
             summary="Refresh access token using refresh token",
             response_model=TokenInfo)
async def refresh_access_token(
        refresh_token: Optional[str] = Cookie(None)
):
    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token not found"
        )

    try:
        payload = decoded_jwt(refresh_token)
        validate_token_type(payload, REFRESH_TOKEN_TYPE)
        user = await get_user_by_token_sub(payload)

        new_access_token = create_access_token(user)

        return TokenInfo(access_token=new_access_token)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )


@router.get("/me/", summary="Get current user data")
def auth_user_check_self_info(
        user_data: SUserWithRole = Depends(get_current_user_with_role_from_access)
) -> dict:
    return {
        "nickname": user_data.nickname,
        "role": user_data.role.name
    }


@router.post("/logout")
def logout(response: Response):
    response.delete_cookie("refresh_token")
    return {"message": "Successfully logged out"}
