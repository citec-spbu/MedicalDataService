from app.dao.base import BaseDAO
from app.series.models import Series


class SeriesDAO(BaseDAO):
    model = Series
