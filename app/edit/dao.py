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
    async def update_patient(cls, patient_id: int, name: Optional[str] = None,
                             birth_date: Optional[date] = None) -> bool:
        """Обновляем данные пациента и связанные метаданные."""
        async with await cls._get_session() as session:
            # Получаем пациента
            patient = await cls.get_patient(patient_id)
            if not patient:
                raise HTTPException(status_code=404, detail="Patient not found")

            # Составляем данные для обновления
            update_data = {}
            if name:
                update_data["name"] = name
            if birth_date:
                update_data["birth_date"] = birth_date

            # Если данные для обновления отсутствуют
            if not update_data:
                raise HTTPException(status_code=400, detail="No data to update")

            # Выполняем обновление данных пациента
            try:
                await session.execute(
                    update(Patient)
                    .where(Patient.id == patient_id)
                    .values(**update_data)
                )

                # Обновление связанных данных в Instance
                query = select(Instance).join(Series).join(Study).where(Study.patient_id == patient_id)
                result = await session.execute(query)
                instances = result.scalars().all()

                # Обновляем метаданные для каждого Instance
                for instance in instances:
                    metadata = instance.metadata_
                    if name:
                        metadata["00100010"]["Value"] = [{"Alphabetic": name}]
                    if birth_date:
                        metadata["00100030"]["Value"] = [birth_date.strftime("%Y%m%d")]

                    await session.execute(
                        update(Instance).where(Instance.id == instance.id).values(metadata_=metadata)
                    )

                # Завершаем транзакцию
                await session.commit()
                return True
            except SQLAlchemyError as e:
                await session.rollback()  # Откат транзакции в случае ошибки
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

            # Составляем данные для обновления
            update_data = {}
            if file_name:
                update_data["file_name"] = file_name
            if upload_date:
                update_data["upload_date"] = upload_date
            if upload_time:
                update_data["upload_time"] = upload_time
            if uploader_id:
                # Проверка существования пользователя перед обновлением
                user_exists = await session.execute(
                    select(User).where(User.id == uploader_id)
                )
                if not user_exists.scalar_one_or_none():
                    raise HTTPException(status_code=404, detail=f"User with id {uploader_id} not found")
                update_data["uploader_id"] = uploader_id

            # Если данных для обновления нет
            if not update_data:
                raise HTTPException(status_code=400, detail="No data to update")

            try:
                # Выполняем обновление данных DICOM файла
                await session.execute(
                    update(DicomFile)
                    .where(DicomFile.id == file_id)
                    .values(**update_data)
                )
                await session.commit()
                return True
            except SQLAlchemyError as e:
                await session.rollback()  # Откат транзакции в случае ошибки
                raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
