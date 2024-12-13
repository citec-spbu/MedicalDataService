from sqlalchemy import select
from app.database import async_session_maker
from app.series.models import Series
from app.studies.models import Study
from app.patients.models import Patient
from app.instances.models import Instance
from app.dicom_file.models import DicomFile
from typing import Optional, Tuple, List
from sqlalchemy.orm import joinedload

class DownloadDAO:
    @classmethod
    async def get_series_info(cls, series_id: int) -> Optional[Tuple[Series, Study, Patient, List[Instance]]]:
        """Получает информацию о series и связанных с ней данных"""
        async with async_session_maker() as session:
            # Составляем запрос для получения всех связанных данных
            query = (
                select(Series, Study, Patient, Instance)
                .options(joinedload(Instance.dicom_file))  # Загружаем связанные DicomFile
                .join(Study, Series.study_id == Study.id)
                .join(Patient, Study.patient_id == Patient.id)
                .join(Instance, Instance.series_id == Series.id)
                .where(Series.id == series_id)
            )

            result = await session.execute(query)
            rows = result.unique().all()  # используем unique() для удаления дубликатов

            if not rows:
                return None

            # Группируем результаты
            series = rows[0][0]  # Series из первой строки
            study = rows[0][1]   # Study из первой строки
            patient = rows[0][2]  # Patient из первой строки
            instances = [row[3] for row in rows]  # Все Instance

            # Убеждаемся, что все данные загружены
            for instance in instances:
                await session.refresh(instance, ['dicom_file'])

            return series, study, patient, instances