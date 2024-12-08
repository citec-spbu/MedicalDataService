from app.dao.base import BaseDAO
from app.studies.models import Study


class StudyDAO(BaseDAO):
    model = Study
