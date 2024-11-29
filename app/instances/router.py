from fastapi import APIRouter, HTTPException
from fastapi.responses import Response
from app.instances.dao import InstanceDAO
from app.config import get_minio_client

router = APIRouter(prefix="/api/instances", tags=["instances"])
minio_client = get_minio_client()

@router.get("/{instance_uid}/pixel-data")
async def get_pixel_data(instance_uid: str):
    instance = await InstanceDAO.find_one_or_none(sop_instance_uid=instance_uid)
    if not instance:
        raise HTTPException(status_code=404, detail="Instance not found")

    try:
        # Получаем пиксельные данные из MinIO
        data = minio_client.get_object(
            "pixel-data",
            instance.pixel_data_path
        ).read()
        
        # Возвращаем как бинарные данные
        return Response(
            content=data,
            media_type="application/octet-stream"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving pixel data: {str(e)}"
        ) 