from pydantic import BaseModel
from typing import List

class DownloadStudiesRequest(BaseModel):
    study_ids: List[int]