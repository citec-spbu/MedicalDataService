from faststream.rabbit.fastapi import RabbitRouter, Logger
from pydantic import BaseModel
from app.config import rabbitmq_settings

router = RabbitRouter(rabbitmq_settings.url)


class IndexQuery(BaseModel):
    user_id: int
    bucket_name: str
    minio_path: str


@router.subscriber("dicom_processing")
async def receive_archive(query: IndexQuery, logger: Logger):
    print("Message from broker queue:")
    print("\t", query.user_id)
    print("\t", query.bucket_name)
    print("\t", query.minio_path)