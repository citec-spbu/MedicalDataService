# Provides work with hashes
from fastapi import (
    HTTPException,
    Form,
    status
)
from typing import Annotated
from passlib.context import CryptContext
from app.users.dao import UserDAO
from app.users.schemas import SUser
from app.users.models import User

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto",
                           truncate_error=True)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


async def authenticate_user(user_data: Annotated[SUser, Form()]) -> User:
    """
    Check if user with nickname and password exists in database
    Update hash if the one in database is deprecated
    :param user_data: user nickname and password
    :return: User
    """
    user = await UserDAO.find_one_or_none(nickname=user_data.nickname)
    if not user or not verify_password(user_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
            headers={"WWW-Authenticate": "Bearer"})
    if pwd_context.needs_update(user.password):
        new_password = get_password_hash(user_data.password)
        user.password = new_password
        await UserDAO.update_hash_by_id(id=user.id, new_hash=new_password)
    return user
