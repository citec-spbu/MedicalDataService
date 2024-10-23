# Provides work with hashes
from passlib.context import CryptContext
from app.users.dao import UserDAO

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto",
                           truncate_error=True)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


async def authenticate_user(nickname: str, password: str):
    user = await UserDAO.find_one_or_none(nickname=nickname)
    if not user or verify_password(plain_password=password,
                                   hashed_password=user.password) is False:
        return None
    return user
