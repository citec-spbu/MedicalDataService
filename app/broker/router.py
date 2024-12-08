from faststream.rabbit.fastapi import (
    RabbitRouter,
    Logger
)
from pydantic import BaseModel
from app.patients.index import index_patient
from app.studies.index import index_study
from app.series.index import index_series
from app.slices.index import index_slice
from app.dicom_file.dao import DicomDao
from app.config import (
    rabbitmq_settings,
    get_minio_client
)
from pydicom import dcmread
from io import BytesIO
from zipfile import ZipFile

router = RabbitRouter(rabbitmq_settings.url)


class DBIndexQuery(BaseModel):
    user_id: int
    bucket_name: str
    minio_path: str


@router.subscriber("DBIndexing")
async def receive_archive(query: DBIndexQuery, logger: Logger):
    minio_client = get_minio_client()
    file = minio_client.get_object(query.bucket_name, query.minio_path)
    file = minio_client.get_object(query.bucket_name, query.minio_path)
    dicom_file_instance_from_db = await DicomDao.find_one_or_none(
        minio_path=query.minio_path
    )
    with ZipFile(BytesIO(file.read())) as zip_file:
        slices_count = {}
        for file_info in zip_file.infolist():
            if not file_info.is_dir():
                ds = dcmread(
                    fp=BytesIO(zip_file.read(file_info.filename)),
                    force=True
                )
                new_patient = await index_patient(ds)
                new_study = await index_study(ds, new_patient.id)
                new_series = await index_series(
                    ds=ds,
                    study_id=new_study.id,
                    dicom_file_id=dicom_file_instance_from_db.id
                )
                if new_series.id not in slices_count:
                    slices_count[new_series.id] = 0
                slices_count[new_series.id] += 1
                await index_slice(
                    ds=ds,
                    series_id=new_series.id,
                    number_in_series=slices_count[new_series.id]
                )
