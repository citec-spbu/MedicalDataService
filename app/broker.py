from faststream.rabbit.fastapi import RabbitRouter, Logger
from pydantic import BaseModel
from app.config import rabbitmq_settings, minio_settings, get_minio_client
import zipfile
import pydicom
from pydicom.uid import JPEGLSLossless
from pydicom.multival import MultiValue
import datetime

from app.patients.dao import PatientDAO
from app.studies.dao import StudyDAO
from app.series.dao import SeriesDAO
from app.instances.dao import InstanceDAO
from app.dicom_file.dao import DicomFileDAO
from io import BytesIO

router = RabbitRouter(rabbitmq_settings.url)

minio_client = get_minio_client();

MINIO_BUCKET = minio_settings.MINIO_BUCKET
MINIO_LOCAL_DOWNLOAD_PATH = minio_settings.MINIO_LOCAL_DOWNLOAD_PATH

PATIENT_FIELDS = {
    "00100010": "name",
    # "00100020": "id",
    # "00100021": "issuer",
    "00100030": "birth_date",
    "00100040": "sex"
}
STUDY_FIELDS = {
    "00081030": "description",
    "00080050": "accession_number",
    "0020000D": "instance_uid",
    "00080020": "date",
    "00080030": "time",
    # "00200010": "id",
    "00080061": "modalities",
    "00201206": "series_count",
    "00201208": "instances_count"
}
SERIES_FIELDS = {
    "0008103E": "description",
    "0020000E": "instance_uid",
    # "00200011": "id",
    "00080060": "modality",
    "00080021": "date",
    "00080031": "time",
    "00080005": "character_set",
    "00080070": "manufacturer",
    "00080090": "physician_name",
    "00081090": "manufacturer_model_name",
    "00201209": "instances_count"
}
INSTANCE_FIELDS = {
    "00080018": "sop_instance_uid"
}

class IndexQuery(BaseModel):
    user_id: int
    bucket_name: str
    minio_path: str


@router.subscriber("dicom_processing")
async def receive_archive(query: IndexQuery, logger: Logger):
    minio_client.fget_object(MINIO_BUCKET, query.minio_path, MINIO_LOCAL_DOWNLOAD_PATH)

    with zipfile.ZipFile(MINIO_LOCAL_DOWNLOAD_PATH, 'r') as archive:
        for file in archive.filelist:
            if file.filename.endswith('/') or file.filename.startswith("DICOMDIR"):
                    continue
            
            ds = pydicom.dcmread(BytesIO(archive.read(file.filename)))
            ds.compress(JPEGLSLossless)

            patient_fields = {}
            for key, value in PATIENT_FIELDS.items():
                patient_fields[value] = ds[key].value if key in ds else None
            if (patient_fields["name"] != None): patient_fields["name"] = str(patient_fields["name"])
            if (patient_fields["birth_date"]): patient_fields["birth_date"] = datetime.datetime.strptime(patient_fields["birth_date"],'%Y%m%d').date()
            patient_fields["issuer"] = "medicalDataService"
            if (not (await PatientDAO.is_exist(**patient_fields))):
                await PatientDAO.add(**patient_fields)

            study_fields = {}
            for key, value in STUDY_FIELDS.items():
                study_fields[value] = ds[key].value if key in ds else None
            study_fields["patient_id"] = (await PatientDAO.find_one_or_none(**patient_fields)).id
            if (study_fields["date"]): study_fields["date"] = datetime.datetime.strptime(study_fields["date"],'%Y%m%d').date()
            if (study_fields["time"]): study_fields["time"] = datetime.datetime.strptime(study_fields["time"],'%H%M%S.%f').time()
            if (not (await StudyDAO.is_exist(instance_uid=study_fields["instance_uid"]))):
                await StudyDAO.add(**study_fields)

            series_fields = {}
            for key, value in SERIES_FIELDS.items():
                series_fields[value] = ds[key].value if key in ds else None
            series_fields["study_id"] = (await StudyDAO.find_one_or_none(instance_uid=study_fields["instance_uid"])).id
            if (series_fields["date"]): series_fields["date"] = datetime.datetime.strptime(series_fields["date"],'%Y%m%d').date()
            if (series_fields["time"]): series_fields["time"] = datetime.datetime.strptime(series_fields["time"],'%H%M%S.%f').time()
            if (series_fields["physician_name"] != None): series_fields["physician_name"] = str(series_fields["physician_name"])
            if (not await SeriesDAO.is_exist(instance_uid=series_fields["instance_uid"])):
                await SeriesDAO.add(**series_fields)

            instance_fields = {}
            for key, value in INSTANCE_FIELDS.items():
                instance_fields[value] = ds[key].value if ds[key] else None
            instance_fields["series_id"] = (await SeriesDAO.find_one_or_none(instance_uid=series_fields["instance_uid"])).id
            instance_fields["dicom_file_id"] = (await DicomFileDAO.find_one_or_none(minio_path=query.minio_path)).id
            instance_fields["check_sum"] = "0" # TODO

            json_metadata = {}
            for field in ds:
                json_metadata |= { field.tag.json_key: { "vr": field.VR } }
                if (field and field.tag.json_key != "7FE00010"):
                    json_metadata[field.tag.json_key] |= { "Value": [ *field.value ] if type(field.value) is MultiValue else [ field.value ] };
            instance_fields["metadata_"] = str(json_metadata)
            if (not await InstanceDAO.is_exist(sop_instance_uid=instance_fields["sop_instance_uid"])):
                await InstanceDAO.add(**instance_fields)
                with open(query.minio_path + instance_fields["sop_instance_uid"], 'wb') as f:
                    f.write(ds.PixelData[20:])

    print("")