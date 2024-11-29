from app.dao.base import BaseDAO
from app.studies.models import Study


class StudyDAO(BaseDAO):
    model = Study

    @classmethod
    async def get_study(cls, instance_uid: str):
        return await cls.find_one_or_none(instance_uid=instance_uid)

    @classmethod
    async def get_patient_studies(cls, patient_id: int):
        return await cls.find_all(patient_id=patient_id) 