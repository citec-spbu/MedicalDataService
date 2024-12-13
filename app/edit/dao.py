from sqlalchemy import select, update
from app.database import async_session_maker
from app.patients.models import Patient
from app.dicom_file.models import DicomFile
from app.instances.models import Instance
from app.series.models import Series
from app.studies.models import Study
from datetime import date, time
from typing import Optional
from fastapi import HTTPException
from sqlalchemy.exc import SQLAlchemyError
from app.users.models import User


class EditDAO:
    @classmethod
    async def get_patient(cls, patient_id: int) -> Optional[Patient]:
        """Данные пациента"""
        async with async_session_maker() as session:
            result = await session.execute(
                select(Patient).where(Patient.id == patient_id)
            )
            return result.scalar_one_or_none()

    @classmethod
    async def get_dicom_file(cls, file_id: int) -> Optional[DicomFile]:
        """Данные DICOM файла"""
        async with async_session_maker() as session:
            result = await session.execute(
                select(DicomFile).where(DicomFile.id == file_id)
            )
            return result.scalar_one_or_none()

    @classmethod
    async def update_patient(cls, patient_id: int, name: Optional[str] = None,
                             birth_date: Optional[date] = None) -> bool:
        """Обновляем данные пациента и связанные метаданные"""
        async with async_session_maker() as session:

            patient = await cls.get_patient(patient_id)
            if not patient:
                return False

            update_data = {}
            if name is not None:
                update_data["name"] = name
            if birth_date is not None:
                update_data["birth_date"] = birth_date

            if update_data:
                await session.execute(
                    update(Patient)
                    .where(Patient.id == patient_id)
                    .values(**update_data)
                )

                query = select(Instance).join(
                    Series, Series.id == Instance.series_id
                ).join(
                    Study, Study.id == Series.study_id
                ).where(Study.patient_id == patient_id)

                result = await session.execute(query)
                instances = result.scalars().all()

                # Обновляем метаданные в каждом instance
                for instance in instances:
                    metadata = instance.metadata_
                    if name is not None:
                        metadata["00100010"]["Value"] = [{"Alphabetic": name}]
                    if birth_date is not None:
                        metadata["00100030"]["Value"] = [birth_date.strftime("%Y%m%d")]

                    await session.execute(
                        update(Instance)
                        .where(Instance.id == instance.id)
                        .values(metadata_=metadata)
                    )

                await session.commit()
                return True
        return False

    @classmethod
    async def update_dicom_file(cls, file_id: int, file_name: Optional[str] = None,
                                upload_date: Optional[date] = None,
                                upload_time: Optional[time] = None,
                                uploader_id: Optional[int] = None) -> bool:
        """Обновляем данные DICOM файла"""
        async with async_session_maker() as session:
            dicom_file = await cls.get_dicom_file(file_id)
            if not dicom_file:
                return False

            update_data = {}

            if file_name is not None:
                update_data["file_name"] = file_name
            if upload_date is not None:
                update_data["upload_date"] = upload_date
            if upload_time is not None:
                update_data["upload_time"] = upload_time
            if uploader_id is not None:
                # Проверяем существование пользователя перед обновлением
                user_exists = await session.execute(
                    select(User).where(User.id == uploader_id)
                )
                if not user_exists.scalar_one_or_none():
                    raise HTTPException(
                        status_code=404,
                        detail=f"User with id {uploader_id} not found"
                    )
                update_data["uploader_id"] = uploader_id

            if update_data:
                try:
                    await session.execute(
                        update(DicomFile)
                        .where(DicomFile.id == file_id)
                        .values(**update_data)
                    )
                    await session.commit()
                    return True
                except SQLAlchemyError as e:
                    await session.rollback()
                    raise HTTPException(
                        status_code=400,
                        detail=str(e)
                    )
        return False 