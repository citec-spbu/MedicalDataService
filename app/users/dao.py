# DAO is data access object. Provide interface for making SQL queries to DB
from fastapi import HTTPException, status
from sqlalchemy import update, select
from sqlalchemy.exc import SQLAlchemyError
from app.dao.base import BaseDAO
from app.users.models import User
from app.database import async_session_maker


class UserDAO(BaseDAO):
    model = User

    @classmethod
    # получение id пользователя по нику
    async def get_user_id_by_nickname(cls, nickname: str) -> int:
        user = await cls.find_one_or_none(nickname=nickname)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        return user.id

    @classmethod
    async def update_hash_by_id(cls, id: int, new_hash: str):
        """
        Update hash password of user by id
        """
        async with async_session_maker() as session:
            query = update(cls.model)\
                .values(password=new_hash).where(cls.model.id == id)
            try:
                await session.execute(query)
                await session.commit()
            except SQLAlchemyError as e:
                await session.rollback()
                raise e
