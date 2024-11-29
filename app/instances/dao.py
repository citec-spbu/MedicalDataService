from app.dao.base import BaseDAO
from app.instances.models import Instance
from app.series.dao import SeriesDAO

class InstanceDAO(BaseDAO):
    model = Instance

    @classmethod
    async def get_all_instances(cls, study_uid: str, series_uid: str):
        series = await SeriesDAO.get_series(study_uid, series_uid)
        return await cls.find_all(series_id=series.id)
    
    @classmethod
    async def get_instance(cls, study_uid: str, series_uid: str, instance_uid):
        series = await SeriesDAO.get_series(study_uid, series_uid)
        return await cls.find_one_or_none(series_id=series.id, sop_instance_uid=instance_uid)

