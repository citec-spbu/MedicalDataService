from app.dao.base import BaseDAO
from app.patients.models import Patient

class PatientDAO(BaseDAO):
    model = Patient

    @classmethod
    async def get_all_patients(cls):
        return await cls.find_all()
    
