from pydantic import BaseModel
from typing import List

class DownloadSeriesRequest(BaseModel):
    series_ids: List[int]