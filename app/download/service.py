from fastapi import HTTPException
from io import BytesIO
import zipfile
import pydicom
import logging
import json
from app.config import get_minio_client, minio_settings
from app.instances.dao import InstanceDAO
from app.dicom_file.dao import DicomFileDAO
from app.series.dao import SeriesDAO
from sqlalchemy import select
from typing import List, Dict

logger = logging.getLogger(__name__)
minio_client = get_minio_client()


class DicomFileProcessor:
    @staticmethod
    async def process_series(series_id: int) -> bytes:
        """Обрабатывает серию и возвращает архив с DICOM файлами"""

        # Проверяем существование серии
        series = await SeriesDAO.find_one_or_none(id=series_id)
        if not series:
            raise HTTPException(status_code=404, detail="Series not found")

        # Получаем все instances для данной серии
        instances = await InstanceDAO.find_all(series_id=series_id)
        if not instances:
            raise HTTPException(status_code=404, detail="No instances found for series")

        logger.info(f"Starting to process {len(instances)} instances")

        # Получаем уникальные dicom_file_ids
        dicom_file_ids = list(set(instance.dicom_file_id for instance in instances))

        # олучаем все dicom файлы для этих instances
        dicom_files = []
        for file_id in dicom_file_ids:
            dicom_file = await DicomFileDAO.find_one_or_none(id=file_id)
            if dicom_file:
                dicom_files.append(dicom_file)

        if not dicom_files:
            raise HTTPException(status_code=404, detail="No DICOM files found")

        # Создаем словарь для быстрого поиска dicom файла по id
        dicom_files_map = {df.id: df for df in dicom_files}

        # Группируем instances по архивам
        archive_instances: Dict[str, List] = {}
        for instance in instances:
            dicom_file = dicom_files_map.get(instance.dicom_file_id)
            if dicom_file:
                if dicom_file.minio_path not in archive_instances:
                    archive_instances[dicom_file.minio_path] = []
                archive_instances[dicom_file.minio_path].append(instance)

        # Создаем выходной архив
        output_buffer = BytesIO()
        with zipfile.ZipFile(output_buffer, 'w', zipfile.ZIP_DEFLATED) as output_zip:

            # Обрабатываем каждый архив
            for archive_path, archive_instances_list in archive_instances.items():
                logger.info(f"Processing archive: {archive_path}")

                try:
                    # Скачиваем архив из MinIO
                    try:
                        response = minio_client.get_object(
                            bucket_name=minio_settings.MINIO_BUCKET,
                            object_name=archive_path
                        )
                        archive_data = BytesIO(response.read())
                        archive_size = archive_data.getbuffer().nbytes
                        logger.info(f"Downloaded archive size: {archive_size} bytes")

                    except Exception as e:
                        logger.error(f"Failed to download archive from MinIO: {str(e)}")
                        continue

                    archive_data.seek(0)
                    logger.info(f"Successfully downloaded archive from MinIO: {archive_path}")

                    # Создаем словарь для быстрого поиска instance по SOP UID
                    instance_by_sop = {}
                    for instance in archive_instances_list:
                        try:
                            # Проверяем тип метаданных и преобразуем их
                            if isinstance(instance.metadata, str):
                                try:
                                    metadata = json.loads(instance.metadata)
                                except json.JSONDecodeError:
                                    logger.error(f"Failed to parse metadata JSON for instance {instance.id}")
                                    continue
                            elif isinstance(instance.metadata, dict):
                                metadata = instance.metadata
                            else:
                                logger.error(
                                    f"Unexpected metadata type for instance {instance.id}: {type(instance.metadata)}")
                                continue

                            # Получаем SOP Instance UID из метаданных
                            sop_uid = metadata.get('00080018', {}).get('Value', [None])[0]
                            if sop_uid:
                                instance_by_sop[sop_uid] = {
                                    'instance': instance,
                                    'metadata': metadata
                                }
                            else:
                                logger.error(f"No SOP Instance UID found for instance {instance.id}")
                        except Exception as e:
                            logger.error(f"Error processing instance metadata: {str(e)}")
                            continue

                    # Открываем скачанный архив
                    with zipfile.ZipFile(archive_data, 'r') as input_zip:
                        file_list = input_zip.namelist()
                        logger.info(f"Files in archive: {file_list}")

                        # Перебираем все файлы в архиве
                        for filename in file_list:
                            if filename.endswith('/') or 'DICOMDIR' in filename.upper():
                                continue

                            try:
                                # Читаем DICOM файл
                                with input_zip.open(filename) as dicom_file:
                                    ds = pydicom.dcmread(dicom_file)
                                    sop_uid = ds.SOPInstanceUID

                                    # Проверяем, принадлежит ли файл нужной серии
                                    if sop_uid in instance_by_sop:
                                        instance_data = instance_by_sop[sop_uid]
                                        instance = instance_data['instance']
                                        metadata = instance_data['metadata']

                                        # Обновляем метаданные если они были изменены
                                        ds = DicomFileProcessor.update_dicom_metadata(ds, metadata)

                                        # Сохраняем обновленный файл во временный буфер
                                        temp_buffer = BytesIO()
                                        ds.save_as(temp_buffer)
                                        temp_buffer.seek(0)

                                        # Добавляем в выходной архив
                                        output_zip.writestr(
                                            f"series_{series_id}/{filename}",
                                            temp_buffer.getvalue()
                                        )
                                        logger.info(f"Added file {filename} to output archive")

                            except Exception as e:
                                logger.error(f"Error processing file {filename}: {str(e)}")
                                continue

                except Exception as e:
                    logger.error(f"Error processing archive {archive_path}: {str(e)}")
                    continue

        # проверяем, что архив не пустой
        output_size = output_buffer.tell()
        if output_size == 0:
            raise HTTPException(status_code=404, detail="No files were processed successfully")

        logger.info(f"Final zip buffer size: {output_size} bytes")
        output_buffer.seek(0)
        return output_buffer.getvalue()

    @staticmethod
    def update_dicom_metadata(ds: pydicom.Dataset, metadata: dict) -> pydicom.Dataset:
        """Обновляет метаданные в DICOM файле"""
        if not metadata:
            return ds

        for tag_str, data in metadata.items():
            if tag_str == "7FE00010":  # Пропускаем pixel data
                continue

            try:
                # Конвертируем строковый тег в кортеж
                group = int(tag_str[:4], 16)
                element = int(tag_str[4:], 16)
                tag = (group, element)

                if isinstance(data, dict) and "Value" in data and data["Value"]:
                    value = data["Value"][0]

                    # Особая обработка для PersonName
                    if data.get("vr") == "PN" and isinstance(value, dict):
                        value = value.get("Alphabetic", "")

                    # Обновляем значение только если тег существует
                    if tag in ds:
                        ds[tag].value = value

            except Exception as e:
                logger.error(f"Error updating tag {tag_str}: {str(e)}")
                continue

        return ds