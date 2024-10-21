# DAO is data access object. Provide interface for making SQL queries to DB
from sqlalchemy.exc import SQLAlchemyError
from app.dao.base import BaseDAO
from app.users.models import User
from app.database import async_session_maker


class UserDAO(BaseDAO):
    model = User

    @classmethod
    async def add(cls, **values):
        async with async_session_maker() as session:
            async with session.begin():
                new_instance = cls.model(**values)
                session.add(new_instance)
                try:
                    await session.commit()
                except SQLAlchemyError as e:
                    await session.rollback()
                    raise e
                return new_instance
