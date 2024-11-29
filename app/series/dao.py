from app.dao.base import BaseDAO
from app.series.models import Series


class SeriesDAO(BaseDAO):
    model = Series

    @classmethod
    async def get_series(cls, instance_uid: str):
        return await cls.find_one_or_none(instance_uid=instance_uid)

    @classmethod
    async def get_study_series(cls, study_id: int):
        return await cls.find_all(study_id=study_id)

    @classmethod
    async def get_series_by_modality(cls, study_id: int, modality: str):
        return await cls.find_all(study_id=study_id, modality=modality) 