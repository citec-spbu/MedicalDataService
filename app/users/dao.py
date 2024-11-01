# DAO is data access object. Provide interface for making SQL queries to DB
from sqlalchemy import update
from sqlalchemy.exc import SQLAlchemyError
from app.dao.base import BaseDAO
from app.users.models import User
from app.database import async_session_maker


class UserDAO(BaseDAO):
    model = User

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
