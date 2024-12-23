from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import Response, StreamingResponse, FileResponse
from sqlalchemy import select
from contextlib import asynccontextmanager
from app.dao.base import BaseDAO
from app.dicom_file.models import DicomFile
from app.instances.models import Instance
from app.studies.models import Study
from app.series.models import Series
from app.patients.models import Patient
from app.config import get_minio_client, minio_settings
from app.users.jwt.current_user import get_current_user_from_access
from app.users.schemas import SUserWithRole
from app.users.models import UserRole
from app.download.schemas import DownloadSeriesRequest
import io
import zipfile
import os
import pydicom
import shutil
import logging

router = APIRouter(prefix="/download", tags=["Download"])

MINIO_BUCKET = minio_settings.MINIO_BUCKET

logger = logging.getLogger(__name__)


# Функция для обновления метаданных DICOM
def update_dicom_metadata(dicom_bytes, new_name, new_birth_date):
    dataset = pydicom.dcmread(io.BytesIO(dicom_bytes), force=True)
    dataset.PatientName = new_name
    dataset.PatientBirthDate = new_birth_date.strftime("%Y%m%d")
    updated_buffer = io.BytesIO()
    dataset.save_as(updated_buffer)
    updated_buffer.seek(0)
    return updated_buffer


@router.post("/")
async def download_studies_archive(
        request: DownloadSeriesRequest,
        user_data: SUserWithRole = Depends(get_current_user_from_access)
):
    # Проверка входящих данных
    series_uids = request.series_uids
    if not series_uids:
        raise HTTPException(
            status_code=400,
            detail="Study IDs must be provided"
        )

    # Проверка доступа
    if user_data.role == UserRole.UPLOADER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient access rights"
        )

    minio_client = get_minio_client()
    output_archive_buffer = io.BytesIO()  # Выходной архив
    temp_dir = "temp_dicom_files"  # Локальная директория для хранения файлов

    try:
        async with BaseDAO.get_session() as session:
            # Запрос для получения instances, dicom_files и данных пациента
            query = select(Instance.dicom_file_id, Instance.dicom_file_name, Patient.name, Patient.birth_date, DicomFile.minio_path). \
                join(DicomFile, Instance.dicom_file_id == DicomFile.id). \
                join(Series, Instance.series_id == Series.id). \
                join(Study, Series.study_id == Study.id). \
                join(Patient, Study.patient_id == Patient.id). \
                where(Series.instance_uid.in_(series_uids))
            result = await session.execute(query)
            records = result.fetchall()

            if not records:
                raise HTTPException(status_code=404, detail="No DICOM files found for the given study IDs")

            # Словарь для хранения путей архивов и файлов внутри них
            archives_dict = {}
            for dicom_file_id, dicom_file_name, patient_name, patient_birth_date, archive_path in records:
                if archive_path not in archives_dict:
                    archives_dict[archive_path] = []
                archives_dict[archive_path].append({
                    "file_name": dicom_file_name,
                    "patient_name": patient_name,
                    "birth_date": patient_birth_date
                })

            # Создаём временную директорию, если она не существует
            if not os.path.exists(temp_dir):
                os.makedirs(temp_dir)

            # Обрабатываем каждый архив из MinIO
            for archive_path, files_info in archives_dict.items():
                # Загружаем архив из MinIO
                try:
                    logger.info("Attempting to load archive from minio")
                    minio_response = minio_client.get_object(MINIO_BUCKET, archive_path)
                    archive_bytes = io.BytesIO(minio_response.read())
                    logger.info("Archive Loaded")
                except Exception as e:
                    raise HTTPException(
                        status_code=500,
                        detail=f"Failed to load archive {archive_path}: {str(e)}"
                    )

                # Распаковываем только нужные файлы
                with zipfile.ZipFile(archive_bytes, 'r') as zip_ref:
                    for file_info in files_info:
                        
                        file_name = file_info["file_name"]
                        logger.info(f"Unpack {file_name}")

                        # Проверяем, существует ли файл в архиве
                        if file_name not in zip_ref.namelist():
                            raise HTTPException(
                                status_code=404,
                                detail=f"File {file_name} not found in archive {archive_path}"
                            )

                        # Извлекаем файл и обновляем метаданные
                        dicom_bytes = zip_ref.read(file_name)
                        updated_dicom = update_dicom_metadata(
                            dicom_bytes,
                            file_info["patient_name"],
                            file_info["birth_date"]
                        )

                        # Сохраняем обновлённый файл локально
                        file_name = file_name.replace("/", os.sep).replace("\\", os.sep)
                        output_path = os.path.join(temp_dir, file_name)

                        # Создаём директории, если их нет
                        os.makedirs(os.path.dirname(output_path), exist_ok=True)
                        with open(output_path, "wb") as f:
                            f.write(updated_dicom.read())

            # Создаём выходной архив
            with zipfile.ZipFile(output_archive_buffer, mode='w', compression=zipfile.ZIP_DEFLATED) as output_zip:
                for root, _, files in os.walk(temp_dir):
                    for file in files:
                        logger.info(f"Repack {file}")
                        file_path = os.path.join(root, file)
                        output_zip.write(file_path, arcname=file)

            output_archive_buffer.seek(0)

            # Удаляем временные файлы и директорию
            if os.path.exists(temp_dir):
                try:
                    shutil.rmtree(temp_dir)
                except Exception as e:
                    raise HTTPException(
                        status_code=500,
                        detail=f"Failed to remove temp directory: {str(e)}"
                    )
                
            logger.info("Return")

            # Возвращаем архив пользователю
            return Response(
                content=output_archive_buffer.read(),
                media_type="application/zip",
                headers={"Content-Disposition": "attachment; filename=studies_archive.zip"}
            )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing the download: {str(e)}"
        )