from app.dao.base import BaseDAO
from app.users.models import User
from app.database import async_session_maker


class UserDAO(BaseDAO):
    model = User

    @classmethod
    async def add_student(cls, **user_data: dict):
        async with async_session_maker() as session:
            async with session.begin():
                new_user = User(**user_data)
                session.add(new_user)
                await session.flush()
                new_student_id = new_user.id
                await session.commit()
                return new_student_id
