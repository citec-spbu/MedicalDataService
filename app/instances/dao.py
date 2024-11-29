from app.dao.base import BaseDAO
from app.instances.models import Instance
from app.series.dao import SeriesDAO

class InstanceDAO(BaseDAO):
    model = Instance

    @classmethod
    async def get_instances_by_series(cls, series_uid: str):
        series = await SeriesDAO.find_one_or_none(instance_uid=series_uid)
        if not series:
            return None
        return await cls.find_all(series_id=series.id)

    @classmethod
    async def get_instance(cls, instance_uid: str):
        return await cls.find_one_or_none(sop_instance_uid=instance_uid) 