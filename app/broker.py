from pydantic import BaseModel

class IndexQuery(BaseModel):
    user_id: int
    bucket_name: str
    minio_path: str