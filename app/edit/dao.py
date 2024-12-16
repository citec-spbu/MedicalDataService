from sqlalchemy import select, update
from app.database import async_session_maker
from app.patients.models import Patient
from app.dicom_file.models import DicomFile
from app.series.models import Series
from app.studies.models import Study
from datetime import date, time
from typing import Optional
from fastapi import HTTPException
from sqlalchemy.exc import SQLAlchemyError
from app.users.models import User


class EditDAO:

    @staticmethod
    async def _get_session():
        """Возвращает сессию для выполнения запросов к БД."""
        return async_session_maker()

    @classmethod
    async def get_patient(cls, patient_id: int) -> Optional[Patient]:
        """Получение данных пациента по его ID."""
        async with await cls._get_session() as session:
            result = await session.execute(
                select(Patient).where(Patient.id == patient_id)
            )
            return result.scalar_one_or_none()

    @classmethod
    async def get_dicom_file(cls, file_id: int) -> Optional[DicomFile]:
        """Получение данных DICOM файла по его ID."""
        async with await cls._get_session() as session:
            result = await session.execute(
                select(DicomFile).where(DicomFile.id == file_id)
            )
            return result.scalar_one_or_none()

    @classmethod
    async def _validate_and_prepare_update_data(cls, session, **kwargs) -> dict:
        """Проверка существования связанных данных и подготовка данных для обновления."""
        update_data = {}

        if 'uploader_id' in kwargs and kwargs['uploader_id'] is not None:
            user_exists = await session.execute(
                select(User).where(User.id == kwargs['uploader_id'])
            )
            if not user_exists.scalar_one_or_none():
                raise HTTPException(status_code=404, detail=f"User with id {kwargs['uploader_id']} not found")
            update_data['uploader_id'] = kwargs['uploader_id']

        for key, value in kwargs.items():
            if key != 'uploader_id' and value is not None:
                update_data[key] = value

        if not update_data:
            raise HTTPException(status_code=400, detail="No data to update")

        return update_data

    @classmethod
    async def update_patient(cls, patient_id: int, name: Optional[str] = None,
                             birth_date: Optional[date] = None) -> bool:
        """Обновляем данные пациента."""
        async with await cls._get_session() as session:
            patient = await cls.get_patient(patient_id)
            if not patient:
                raise HTTPException(status_code=404, detail="Patient not found")

            update_data = {}
            if name:
                update_data["name"] = name
            if birth_date:
                update_data["birth_date"] = birth_date

            if not update_data:
                raise HTTPException(status_code=400, detail="No data to update")

            try:
                await session.execute(
                    update(Patient)
                    .where(Patient.id == patient_id)
                    .values(**update_data)
                )
                await session.commit()
                return True
            except SQLAlchemyError as e:
                await session.rollback()
                raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

    @classmethod
    async def update_dicom_file(cls, file_id: int, file_name: Optional[str] = None,
                                upload_date: Optional[date] = None,
                                upload_time: Optional[time] = None,
                                uploader_id: Optional[int] = None) -> bool:
        """Обновляем данные DICOM файла."""
        async with await cls._get_session() as session:
            dicom_file = await cls.get_dicom_file(file_id)
            if not dicom_file:
                raise HTTPException(status_code=404, detail="DICOM file not found")

            try:
                update_data = await cls._validate_and_prepare_update_data(
                    session,
                    file_name=file_name,
                    upload_date=upload_date,
                    upload_time=upload_time,
                    uploader_id=uploader_id
                )

                await session.execute(
                    update(DicomFile)
                    .where(DicomFile.id == file_id)
                    .values(**update_data)
                )
                await session.commit()
                return True
            except SQLAlchemyError as e:
                await session.rollback()
                raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
