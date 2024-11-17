from app.dao.base import BaseDAO
from app.patients.models import Patient


class PatientDAO(BaseDAO):
    model = Patient
