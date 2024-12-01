from fastapi import APIRouter, Response
from app.patients.dao import PatientDAO
from app.studies.dao import StudyDAO
from app.series.dao import SeriesDAO
from app.instances.dao import InstanceDAO
from urllib3.filepost import encode_multipart_formdata, choose_boundary
from urllib3.fields import RequestField
from app.config import get_minio_client

router = APIRouter(prefix="/dicomweb", tags=["Access for dicom images and metadata"])

minio_client = get_minio_client()

@router.get("/patients")
@router.get("/patients/metadata")
async def get_patients():
    patients = await PatientDAO.get_all_patients()
    return [patient.to_json() for patient in patients]


@router.get("/studies")
@router.get("/studies/metadata")
async def get_studies(patient_id: int | None = None):
    studies = await StudyDAO.get_patient_studies(patient_id=patient_id) if patient_id else\
              await StudyDAO.get_studies()
    return [dict(study.to_json(), **(await PatientDAO.find_one_or_none(id=study.patient_id)).to_json()) for study in studies]

@router.get("/studies/{study_uid}")
@router.get("/studies/{study_uid}/metadata")
async def get_study(study_uid: str):
    study = await StudyDAO.get_study(instance_uid=study_uid)
    return dict(study.to_json(), **(await PatientDAO.find_one_or_none(id=study.patient_id)).to_json())

@router.get("/studies/{study_uid}/series")
@router.get("/studies/{study_uid}/series/metadata")
async def get_study_series(study_uid: str, modality: str | None = None):
    study = await StudyDAO.get_study(instance_uid=study_uid)
    all_series = await SeriesDAO.get_series_by_modality(study_uid=study_uid, modality=modality) if modality else\
             await SeriesDAO.get_study_series(study_uid=study_uid)

    return [dict(series.to_json(), **{tag: study.to_json()[tag] for tag in ["00081030", "0020000D"]}) for series in all_series]

# @router.get("/studies/{study_uid}/series/{series_uid}")
# @router.get("/studies/{study_uid}/series/{series_uid}/metadata")
# async def get_series(study_uid: str, series_uid: str):
#     study = await StudyDAO.get_study(instance_uid=study_uid)
#     series = await SeriesDAO.get_series(study_uid=study_uid, series_uid=series_uid)

#     return dict(series.to_json(), **{tag: study.to_json()[tag] for tag in ["00081030", "0020000D"]})

# @router.get("/studies/{study_uid}/series/{series_uid}/instances")
# @router.get("/studies/{study_uid}/series/{series_uid}/instances/metadata")
# async def get_instances(study_uid: str, series_uid: str):
#     instances = await InstanceDAO.get_instances(study_uid=study_uid, series_uid=series_uid)
#     return [instance.metadata_ for instance in instances]

@router.get("/studies/{study_uid}/series/{series_uid}/metadata")
async def get_series(study_uid: str, series_uid: str):
    instances = await InstanceDAO.get_instances(study_uid=study_uid, series_uid=series_uid)
    return [instance.metadata_ for instance in instances]

@router.get("/studies/{study_uid}/series/{series_uid}/instances/{instance_uid}")
@router.get("/studies/{study_uid}/series/{series_uid}/instances/{instance_uid}/metadata")
async def get_instance(study_uid: str, series_uid: str, instance_uid: str):
    return (await InstanceDAO.get_instance(study_uid=study_uid, series_uid=series_uid, instance_uid=instance_uid)).metadata_

@router.get("/studies/{study_uid}/series/{series_uid}/instances/{instance_uid}/frames/1")
async def get_instance_pixeldata(study_uid: str, series_uid: str, instance_uid: str):
    instance = await InstanceDAO.get_instance(study_uid=study_uid, series_uid=series_uid, instance_uid=instance_uid)

    data = minio_client.get_object(
            "pixel-data",
            instance.pixel_data_path
        ).read()
    
    boundary = choose_boundary()

    body, _ = encode_multipart_formdata(
        [RequestField(
            name="",
            data=data,
            headers={'Content-Type': "image/jls;transfer-syntax=1.2.840.10008.1.2.4.80"},
        )], boundary)

    return Response(
        content=body,
        media_type="multipart/related"
    )