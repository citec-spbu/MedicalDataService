from sqlalchemy.future import select
from app.database import async_session_maker
from app.deferred_operations.models import DeferredOperation
from app.dicom_file.models import DicomFile
from app.patients.models import Patient
from app.series.models import Series
from app.slices.models import Slice
from app.studies.models import Study
from app.users.models import User
from sqlalchemy.exc import SQLAlchemyError


class BaseDAO:
    model = None

    @classmethod
    async def find_one_or_none(cls, **filter_by):
        """
        Returns one record from a table or None
        """
        async with async_session_maker() as session:
            query = select(cls.model).filter_by(**filter_by)
            result = await session.execute(query)
            return result.scalar_one_or_none()

    @classmethod
    async def add(cls, **values):
        """
        Add new record to table
        """
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
