from app.dao.base import BaseDAO
from app.slices.models import Slice


class SliceDAO(BaseDAO):
    model = Slice
