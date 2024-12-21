from pydantic import BaseModel
from typing import List

class DownloadSeriesRequest(BaseModel):
    series_uids: List[str]