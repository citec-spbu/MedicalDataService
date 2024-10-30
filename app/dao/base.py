from sqlalchemy.future import select
from app.database import async_session_maker
from app.Deferred_operations.models import DeferredOperation
from app.Dicom_file.models import DicomFile
from app.Patients.models import Patient
from app.Series.models import Series
from app.Slices.models import Slice
from app.Studies.models import Study
from app.users.models import User


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
