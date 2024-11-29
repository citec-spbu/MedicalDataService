from faststream.rabbit.fastapi import RabbitRouter, Logger
from pydantic import BaseModel
from app.config import rabbitmq_settings, minio_settings, get_minio_client
import zipfile
import pydicom
from pydicom.uid import JPEGLSLossless
from pydicom.multival import MultiValue
from datetime import datetime
import hashlib
import tempfile
import os
from pathlib import Path
from io import BytesIO
import asyncio
import signal
import logging

#логгер
logger = logging.getLogger(__name__)

from app.patients.dao import PatientDAO
from app.studies.dao import StudyDAO
from app.series.dao import SeriesDAO
from app.instances.dao import InstanceDAO
from app.dicom_file.dao import DicomFileDAO
from app.broker import IndexQuery

#создаем роутер
router = RabbitRouter(rabbitmq_settings.url)

minio_client = get_minio_client()
PIXEL_DATA_BUCKET = "pixel-data"


class DicomProcessor:
    @staticmethod
    def calculate_checksum(data: bytes) -> str:
        return hashlib.sha256(data).hexdigest()

    @staticmethod
    def store_pixel_data(instance_uid: str, pixel_data: bytes) -> str:
        """Сохраняет пиксельные данные в MinIO и возвращает путь"""
        path = f"pixel_data/{instance_uid}.raw"
        try:
            minio_client.put_object(
                PIXEL_DATA_BUCKET,
                path,
                BytesIO(pixel_data),
                length=len(pixel_data)
            )
            return path
        except Exception as e:
            logger.error(f"Error storing pixel data: {str(e)}")
            return None

    @staticmethod
    def _convert_to_json_serializable(value):
        """Конвертирует значения DICOM в JSON-сериализуемый формат"""
        if isinstance(value, (bytes, bytearray)):
            return f"Binary data ({len(value)} bytes)"
        elif hasattr(value, 'original_string'):  # Для PersonName
            return str(value)
        elif isinstance(value, MultiValue):
            return [DicomProcessor._convert_to_json_serializable(v) for v in value]
        elif hasattr(value, 'value'):  # Для других специальных типов DICOM
            return str(value.value)
        else:
            return str(value)

    @staticmethod
    async def process_dicom_file(ds: pydicom.dataset.FileDataset, dicom_file_id: int):
        # проверяем, что это не DICOMDIR и есть необходимые теги
        if not all(hasattr(ds, attr) for attr in ['StudyInstanceUID', 'SeriesInstanceUID', 'SOPInstanceUID']):
            raise ValueError("Missing required DICOM attributes")

        # обработка Patient
        patient_data = {
            "name": str(ds.PatientName) if hasattr(ds, 'PatientName') else None,
            "sex": ds.PatientSex if hasattr(ds, 'PatientSex') else None,
            "birth_date": datetime.strptime(ds.PatientBirthDate, '%Y%m%d').date()
            if hasattr(ds, 'PatientBirthDate') and ds.PatientBirthDate else None,
            "issuer": "medicalDataService"
        }

        if not await PatientDAO.is_exist(**patient_data):
            patient = await PatientDAO.add(**patient_data)
        else:
            patient = await PatientDAO.find_one_or_none(**patient_data)

        # обработка Study
        study_data = {
            "instance_uid": ds.StudyInstanceUID,
            "patient_id": patient.id,
            "description": ds.StudyDescription if hasattr(ds, 'StudyDescription') else None,
            "accession_number": ds.AccessionNumber if hasattr(ds, 'AccessionNumber') else None,
            "date": datetime.strptime(ds.StudyDate, '%Y%m%d').date()
            if hasattr(ds, 'StudyDate') and ds.StudyDate else None,
            "time": datetime.strptime(ds.StudyTime.split('.')[0], '%H%M%S').time()
            if hasattr(ds, 'StudyTime') and ds.StudyTime else None
        }

        if not await StudyDAO.is_exist(instance_uid=study_data["instance_uid"]):
            study = await StudyDAO.add(**study_data)
        else:
            study = await StudyDAO.find_one_or_none(instance_uid=study_data["instance_uid"])

        # обработка Series
        series_data = {
            "instance_uid": ds.SeriesInstanceUID,
            "study_id": study.id,
            "description": ds.SeriesDescription if hasattr(ds, 'SeriesDescription') else None,
            "modality": ds.Modality if hasattr(ds, 'Modality') else None,
            "date": datetime.strptime(ds.SeriesDate, '%Y%m%d').date()
            if hasattr(ds, 'SeriesDate') and ds.SeriesDate else None,
            "time": datetime.strptime(ds.SeriesTime.split('.')[0], '%H%M%S').time()
            if hasattr(ds, 'SeriesTime') and ds.SeriesTime else None,
            "character_set": ds.SpecificCharacterSet if hasattr(ds, 'SpecificCharacterSet') else None,
            "manufacturer": ds.Manufacturer if hasattr(ds, 'Manufacturer') else None,
            "physician_name": str(ds.PerformingPhysicianName) if hasattr(ds, 'PerformingPhysicianName') else None,
            "manufacturer_model_name": ds.ManufacturerModelName if hasattr(ds, 'ManufacturerModelName') else None
        }

        if not await SeriesDAO.is_exist(instance_uid=series_data["instance_uid"]):
            series = await SeriesDAO.add(**series_data)
        else:
            series = await SeriesDAO.find_one_or_none(instance_uid=series_data["instance_uid"])

        # извекаем пиксельные данные
        pixel_data = None
        if hasattr(ds, 'PixelData'):
            try:
                pixel_data = ds.PixelData
            except Exception as e:
                logger.error(f"Error extracting pixel data: {str(e)}")

        # создаем метаданные в формате JSON
        json_metadata = {}
        for field in ds:
            if field.tag.json_key != "7FE00010":
                try:
                    value = DicomProcessor._convert_to_json_serializable(field.value)
                    json_metadata[field.tag.json_key] = {
                        "vr": field.VR,
                        "Value": [value] if not isinstance(value, list) else value
                    }
                except Exception as e:
                    logger.error(f"Error processing metadata field {field.tag}: {str(e)}")

        # сохраняем пиксельные данные в MinIO
        pixel_data_path = None
        if pixel_data:
            pixel_data_path = DicomProcessor.store_pixel_data(
                ds.SOPInstanceUID,
                pixel_data
            )

        # создаем запись в БД
        instance_data = {
            "sop_instance_uid": ds.SOPInstanceUID,
            "series_id": series.id,
            "dicom_file_id": dicom_file_id,
            "check_sum": DicomProcessor.calculate_checksum(pixel_data) if pixel_data else None,
            "metadata_": json_metadata,
            "pixel_data_path": pixel_data_path
        }

        await InstanceDAO.add(**instance_data)


@router.subscriber("dicom_processing")
async def process_archive(query: IndexQuery, logger: Logger):
    logger.info(f"Starting processing archive: {query.minio_path}")

    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            zip_path = os.path.join(temp_dir, "archive.zip")

            # скачиваем архив
            logger.info("Downloading archive from MinIO")
            minio_client.fget_object(query.bucket_name, query.minio_path, zip_path)

            # обрабатываем файлы
            with zipfile.ZipFile(zip_path, 'r') as archive:
                for file in archive.filelist:
                    if file.filename.endswith('/') or 'DICOMDIR' in file.filename.upper():
                        continue

                    logger.info(f"Processing file: {file.filename}")

                    try:
                        # читаем DICOM файл
                        dicom_data = archive.read(file.filename)
                        ds = pydicom.dcmread(BytesIO(dicom_data))

                        # получаем ID файла из базы
                        dicom_file = await DicomFileDAO.find_one_or_none(minio_path=query.minio_path)
                        if not dicom_file:
                            logger.error(f"DicomFile not found for path: {query.minio_path}")
                            continue

                        # Обрабатываем файл
                        await DicomProcessor.process_dicom_file(ds, dicom_file.id)
                        logger.info(f"Successfully processed file: {file.filename}")
                    except Exception as e:
                        logger.error(f"Error processing file {file.filename}: {str(e)}")
                        continue

            logger.info("Archive processing completed")

    except Exception as e:
        logger.error(f"Error processing archive: {str(e)}")
        raise