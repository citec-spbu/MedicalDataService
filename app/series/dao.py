from app.dao.base import BaseDAO
from app.series.models import Series
from app.studies.dao import StudyDAO


class SeriesDAO(BaseDAO):
    model = Series

    @classmethod
    async def get_series(cls, study_uid:str, series_uid: str):
        study = await StudyDAO.get_study(study_uid)
        return await cls.find_one_or_none(study_id=study.id, instance_uid=series_uid)

    @classmethod
    async def get_study_series(cls, study_uid: str):
        study = await StudyDAO.get_study(study_uid)
        return await cls.find_all(study_id=study.id)

    @classmethod
    async def get_series_by_modality(cls, study_uid: str, modality: str):
        study = await StudyDAO.get_study(study_uid)
        return await cls.find_all(study_id=study.id, modality=modality)