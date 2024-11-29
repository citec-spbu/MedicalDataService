from app.dao.base import BaseDAO
from app.studies.models import Study

class StudyDAO(BaseDAO):
    model = Study

    @classmethod
    async def get_study(cls, study_uid: str):
        return await cls.find_one_or_none(instance_uid=study_uid)

    @classmethod
    async def get_studies_by_patient_id(cls, patient_id: int):
        return await cls.find_all(patient_id=patient_id)
    
    @classmethod
    async def get_all_studies(cls):
        return await cls.find_all()

