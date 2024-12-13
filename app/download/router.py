from fastapi import APIRouter, HTTPException
from fastapi.responses import Response
from app.download.service import DicomFileProcessor

router = APIRouter(
    prefix="/download",
    tags=["download"]
)

@router.get("/series/{series_id}")
async def download_series(series_id: int):
    """Скачать DICOM файлы серии"""
    try:
        # Используем правильный метод process_series вместо process_and_package_files
        zip_data = await DicomFileProcessor.process_series(series_id)
        return Response(
            content=zip_data,
            media_type="application/zip",
            headers={
                "Content-Disposition": f"attachment; filename=series_{series_id}.zip"
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing series: {str(e)}")