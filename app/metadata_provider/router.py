from fastapi import APIRouter, Response, HTTPException, Depends, Query
from app.patients.dao import PatientDAO
from app.studies.dao import StudyDAO
from app.series.dao import SeriesDAO
from app.instances.dao import InstanceDAO
from urllib3.filepost import encode_multipart_formdata, choose_boundary
from urllib3.fields import RequestField
from app.config import get_minio_client, minio_settings
from PIL import Image
from typing import Optional
import io
import numpy as np
import pillow_jpls
from app.users.jwt.current_user import get_current_user_from_access
from app.users.models import UserRole, User
from app.users.schemas import SUserWithRole

router = APIRouter(prefix="/dicomweb", tags=["Access for dicom images and metadata"])

minio_client = get_minio_client()

PIXEL_DATA_BUCKET =  minio_settings.MINIO_BUCKET


def anonymize_patient_data(patient_json: dict, show_personal_data: bool = False) -> dict:
    if not show_personal_data:
        if "00100010" in patient_json:
            patient_json["00100010"]["Value"] = [{"Alphabetic": "ANONYMOUS"}]
    return patient_json


@router.get("/patients")
@router.get("/patients/metadata")
async def get_patients(
        user_data: SUserWithRole = Depends(get_current_user_from_access),
        show_personal_data: bool = Query(False, description="Show personal data (requires MODERATOR or ADMIN role)")
):
    if show_personal_data and user_data.role not in [UserRole.MODERATOR, UserRole.ADMIN]:
        raise HTTPException(
            status_code=403,
            detail="Insufficient permissions to view personal data"
        )

    patients = await PatientDAO.get_all_patients()
    return [anonymize_patient_data(patient.to_json(), show_personal_data) for patient in patients]


@router.get("/studies")
@router.get("/studies/metadata")
async def get_studies(
        user_data: SUserWithRole = Depends(get_current_user_from_access),
        patient_id: int | None = None,
        show_personal_data: bool = Query(False, description="Show personal data (requires MODERATOR or ADMIN role)")
):
    if show_personal_data and user_data.role not in [UserRole.MODERATOR, UserRole.ADMIN]:
        raise HTTPException(
            status_code=403,
            detail="Insufficient permissions to view personal data"
        )

    studies = await StudyDAO.get_patient_studies(patient_id=patient_id) if patient_id else \
        await StudyDAO.get_studies()

    return [
        dict(
            study.to_json(),
            **anonymize_patient_data((await PatientDAO.find_one_or_none(id=study.patient_id)).to_json(),
                                     show_personal_data)
        )
        for study in studies
    ]


@router.get("/studies/{study_uid}")
@router.get("/studies/{study_uid}/metadata")
async def get_study(
        study_uid: str,
        user_data: SUserWithRole = Depends(get_current_user_from_access),
        show_personal_data: bool = Query(False, description="Show personal data (requires MODERATOR or ADMIN role)")
):
    if show_personal_data and user_data.role not in [UserRole.MODERATOR, UserRole.ADMIN]:
        raise HTTPException(
            status_code=403,
            detail="Insufficient permissions to view personal data"
        )

    study = await StudyDAO.get_study(instance_uid=study_uid)
    if not study:
        raise HTTPException(status_code=404, detail="Study not found")

    patient = await PatientDAO.find_one_or_none(id=study.patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    return dict(study.to_json(), **anonymize_patient_data(patient.to_json(), show_personal_data))


@router.get("/studies/{study_uid}/series")
@router.get("/studies/{study_uid}/series/metadata")
async def get_study_series(
        study_uid: str,
        modality: str | None = None,
        user_data: SUserWithRole = Depends(get_current_user_from_access)
):
    study = await StudyDAO.get_study(instance_uid=study_uid)
    if not study:
        raise HTTPException(status_code=404, detail="Study not found")

    all_series = await SeriesDAO.get_series_by_modality(study_uid=study_uid, modality=modality) if modality else \
        await SeriesDAO.get_study_series(study_uid=study_uid)

    if not all_series:
        return []

    return [dict(series.to_json(), **{tag: study.to_json()[tag] for tag in ["00081030", "0020000D"]}) for series in
            all_series]


@router.get("/studies/{study_uid}/series/{series_uid}")
@router.get("/studies/{study_uid}/series/{series_uid}/metadata")
@router.get("/studies/{study_uid}/series/{series_uid}/instances")
@router.get("/studies/{study_uid}/series/{series_uid}/instances/metadata")
async def get_series_instances(
        study_uid: str,
        series_uid: str,
        user_data: SUserWithRole = Depends(get_current_user_from_access)
):
    try:
        series = await SeriesDAO.get_series(study_uid=study_uid, series_uid=series_uid)
        if not series:
            raise HTTPException(status_code=404, detail="Series not found")

        instances = await InstanceDAO.get_instances(study_uid=study_uid, series_uid=series_uid)
        return [instance.metadata_ for instance in instances] if instances else []
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving instances: {str(e)}")


@router.get("/studies/{study_uid}/series/{series_uid}/instances/{instance_uid}/metadata")
async def get_instance_metadata(study_uid: str, series_uid: str, instance_uid: str):
    try:
        # Извлекаем конкретный экземпляр
        instance = await InstanceDAO.get_instance(study_uid=study_uid, series_uid=series_uid, instance_uid=instance_uid)
        if not instance:
            raise HTTPException(status_code=404, detail="Instance not found")

        # Извлекаем серию и проверяем, что она существует
        series = await SeriesDAO.get_series(study_uid=study_uid, series_uid=series_uid)
        if not series:
            raise HTTPException(status_code=404, detail="Series not found")

        # Извлекаем информацию о пациенте
        patient = await PatientDAO.find_one_or_none(id=series.patient_id)
        if not patient:
            raise HTTPException(status_code=404, detail="Patient not found")

        # Добавляем имя и дату рождения пациента в метадату экземпляра
        return dict(instance.metadata_, patient_name=patient.name, patient_birth_date=patient.birth_date)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving instance metadata: {str(e)}")


@router.get("/studies/{study_uid}/series/{series_uid}/instances/{instance_uid}/frames/1")
async def get_instance_pixeldata(
        study_uid: str,
        series_uid: str,
        instance_uid: str,
        user_data: SUserWithRole = Depends(get_current_user_from_access)
):
    instance = await InstanceDAO.get_instance(study_uid=study_uid, series_uid=series_uid, instance_uid=instance_uid)
    if not instance:
        raise HTTPException(status_code=404, detail="Instance not found")

    try:
        data = minio_client.get_object(
            PIXEL_DATA_BUCKET,
            instance.pixel_data_path
        ).read()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving pixel data: {str(e)}")

    boundary = choose_boundary()

    body, _ = encode_multipart_formdata(
        [RequestField(
            name="",
            data=data,
            headers={'Content-Type': "image/jls;transfer-syntax=1.2.840.10008.1.2.4.80"},
        )], boundary)

    return Response(
        content=body,
        media_type=f"multipart/related; boundary={boundary}"
    )


async def create_preview(pixel_data: bytes, metadata: Optional[dict] = None) -> bytes:
    """
    Создаёт превью изображения из пиксельных данных.
    """
    image = Image.open(io.BytesIO(pixel_data))

    # Проверяем наличие WindowCenter в метаданных
    has_window_center = metadata.get('00281050', {}).get('Value') is not None if metadata else False

    # Проверяем режим изображения и наличие floating pixels
    is_grayscale = image.mode == 'L'
    has_transparency = 'A' in image.mode

    if has_window_center or is_grayscale or has_transparency:
        if image.mode != 'L':
            image = image.convert('L')

        image = Image.eval(image, lambda x: 255 - x)

    original_size = image.size
    aspect_ratio = original_size[0] / original_size[1]

    if aspect_ratio > 1:
        preview_size = (256, int(256 / aspect_ratio))
    else:
        preview_size = (int(256 * aspect_ratio), 256)

    preview_image = image.resize(preview_size, Image.Resampling.LANCZOS)

    background = Image.new('RGB', (256, 256), 'black')

    x = (256 - preview_size[0]) // 2
    y = (256 - preview_size[1]) // 2

    background.paste(preview_image, (x, y))

    preview_buffer = io.BytesIO()
    background.save(preview_buffer, format='WEBP')
    preview_buffer.seek(0)

    return preview_buffer.getvalue()


@router.get("/studies/{study_uid}/series/{series_uid}/instances/{instance_uid}/preview")
async def get_instance_preview(study_uid: str, series_uid: str, instance_uid: str):
    """
    Создаёт превью изображения для конкретного экземпляра.
    """
    instance = await InstanceDAO.get_instance(study_uid=study_uid, series_uid=series_uid, instance_uid=instance_uid)
    if not instance:
        raise HTTPException(status_code=404, detail="Instance not found")

    try:
        pixel_data = minio_client.get_object(
            PIXEL_DATA_BUCKET,
            instance.pixel_data_path
        ).read()

        preview = await create_preview(pixel_data, instance.metadata_)
        return Response(content=preview, media_type="image/png")

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error creating preview: {str(e)}"
        )


@router.get("/studies/{study_uid}/series/{series_uid}/preview")
async def get_series_preview(study_uid: str, series_uid: str):
    """
    Создаёт превью изображения для первой серии.
    """
    try:
        instances = await InstanceDAO.get_instances(study_uid=study_uid, series_uid=series_uid)
        if not instances:
            raise HTTPException(status_code=404, detail="No instances found")

        instance = instances[0]
        pixel_data = minio_client.get_object(
            PIXEL_DATA_BUCKET,
            instance.pixel_data_path
        ).read()

        preview = await create_preview(pixel_data, instance.metadata_)
        return Response(content=preview, media_type="image/png")

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error creating preview: {str(e)}"
        )
