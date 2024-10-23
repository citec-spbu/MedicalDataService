# Router describes internal logic for working on each user URL
# request that starts with a certain prefix
from fastapi import APIRouter, HTTPException, status
from app.users.dao import UserDAO
from app.users.schemas import SUser
from app.users.auth import get_password_hash, authenticate_user


router = APIRouter(prefix="/user", tags=["Authorization and registration"])


# TODO Maybe allow only certain characters in the password and nickname
@router.post("/register/", summary="Register a new user")
async def register_user(user_data: SUser) -> dict:
    user = await UserDAO.find_one_or_none(nickname=user_data.nickname)
    if user is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"The user '{user_data.nickname}' already exists")
    user_dict = user_data.dict()
    user_dict["password"] = get_password_hash(user_data.password)
    await UserDAO.add(**user_dict)
    return {"message": "You have registered successfully!"}


# TODO maybe add cookie and access token support
@router.post("/login/", summary="Login to an existing account")
async def auth_user(user_data: SUser):
    check = await authenticate_user(nickname=user_data.nickname,
                                    password=user_data.password)
    if check is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Wrong nickname or password")
    return {"message": "Logged in successfully"}


# TODO delete request later
@router.get("/exist/", summary="Check if user exists in DB")
async def check_existence_user(nickname: str) -> dict:
    user = await UserDAO.find_one_or_none(nickname=nickname)
    if user is None:
        return {"message": f"The user '{nickname}' does not exist"}
    return {"message": f"The user '{nickname}' exists in the database"}
