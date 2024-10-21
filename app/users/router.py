# Router describes internal logic for working on each user URL
# request that starts with a certain prefix
from fastapi import APIRouter, HTTPException, status
from app.users.dao import UserDAO
from app.users.schemas import SUserRegister
from app.users.auth import get_password_hash


router = APIRouter(prefix="/user", tags=["Authorization and registration"])


# TODO Maybe allow only certain characters in the password and nickname
@router.post("/register/")
async def register_user(user_data: SUserRegister) -> dict:
    user = await UserDAO.find_one_or_none(nickname=user_data.nickname)
    if user is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"User with nickname {user_data.nickname} already exists")
    user_dict = user_data.dict()
    user_dict["password"] = get_password_hash(user_data.password)
    await UserDAO.add(**user_dict)
    return {"message": "You have registered successfully!"}
