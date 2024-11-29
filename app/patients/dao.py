from app.dao.base import BaseDAO
from app.patients.models import Patient


class PatientDAO(BaseDAO):
    model = Patient

    @classmethod
    async def get_patient(cls, name: str, issuer: str):
        return await cls.find_one_or_none(name=name, issuer=issuer)

    @classmethod
    async def get_all_patients(cls):
        return await cls.find_all() 