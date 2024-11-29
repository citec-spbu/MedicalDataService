from fastapi import (
    APIRouter,
    Response
)

from app.patients.dao import PatientDAO
from app.studies.dao import StudyDAO
from app.series.dao import SeriesDAO
from app.instances.dao import InstanceDAO
# from requests_toolbelt import MultipartEncoder
# from pydicom import dcmread
# from pydicom.uid import JPEGLSLossless
# from pydicom.multival import MultiValue
# from pydicom.datadict import dictionary_VR
# from os import listdir

# imageFiles = "C://Users/Maxx/Desktop/test_data/BVL250941/"

# files = [f for f in listdir(imageFiles)]
# studyFields = [
#     "00080020",
#     "00080030",
#     "00080050",
#     "00080050",
#     "00080056",
#     "00080061",
#     "00080090",
#     "00080201",
#     "00081190",
#     "00100010",
#     "00100020",
#     "00100030",
#     "00100040",
#     "0020000D",
#     "00200010",
#     "00201206",
#     "00201208"
# ]

# seriesFields = [
#     "00080060",
#     "00080201",
#     "0008103E",
#     "00081190",
#     "0020000E",
#     "00200011",
#     "00201209",
#     "00400244",
#     "00400245",
#     "00400275",
# ]

# instanceFields = [
#     "00080016",
#     "00080018",
#     "00080056",
#     "00080060",
#     "00080201",
#     "00081190",
#     "0020000E",
#     "00200013",
#     "00280008",
#     "00280010",
#     "00280011",
#     "00280030",
#     "00280100",
#     "00281050",
#     "00281051"
# ]

# studies = []
# series = []
# instances = []
# instancesPixelData = {}

# for file in files:
#     ds = dcmread(imageFiles + file)
#     ds.compress(JPEGLSLossless)

#     if not next((x for x in studies if x["0020000D"]["Value"][0] == ds["0020000D"].value), None):
#         study = { }
#         for field in studyFields:
#             study |= { field: { "vr": dictionary_VR(field) } }
#             if (field in ds) :
#                 study[field] |= { "Value": ds[field].value if type(ds[field].value) is MultiValue else [ ds[field].value ] };
#         studies.append(study)

#     if not next((x for x in series if x["0020000E"]["Value"][0] == ds["0020000E"].value), None):
#         serie = { }
#         for field in seriesFields:
#             serie |= { field: { "vr": dictionary_VR(field) } }
#             if (field in ds):
#                 serie[field] |= { "Value": ds[field].value if type(ds[field].value) is MultiValue else [ ds[field].value ] };
#         series.append(serie)

#     if not next((x for x in instances if x["00080018"]["Value"][0] == ds["00080018"].value), None):
#         instancesPixelData[ds["00080018"].value] = ds.PixelData[20:];

#         instance = { }
#         for field in ds:
#             instance |= { field.tag.json_key: { "vr": field.VR } }
#             if (field and field.tag.json_key != "7FE00010"):
#                 instance[field.tag.json_key] |= { "Value": [ *field.value ] if type(field.value) is MultiValue else [ field.value ] };
#         instances.append(instance)
        

router = APIRouter(prefix="/dicomweb", tags=["Access for dicom images and metadata"])

@router.get("/patients")
async def get_all_patients():
    return await PatientDAO.get_all_patients()

@router.get("/studies")
@router.get("/studies/metadata")
async def get_all_studies(patient_id: int | None = None):
    if patient_id:
        return await StudyDAO.get_studies_by_patient_id(patient_id=patient_id)
    return await StudyDAO.get_all_studies()

@router.get("/studies/{study_uid}")
@router.get("/studies/{study_uid}/metadata")
async def get_study(study_uid: str):
    return await StudyDAO.get_study(study_uid)

@router.get("/studies/{study_uid}/series")
@router.get("/studies/{study_uid}/series/metadata")
async def get_all_series(study_uid: str):
    return await SeriesDAO.get_all_series(study_uid)

@router.get("/studies/{study_uid}/series/{series_uid}")
@router.get("/studies/{study_uid}/series/{series_uid}/metadata")
async def get_series(study_uid: str, series_uid: str):
    return await SeriesDAO.get_series(study_uid, series_uid)

@router.get("/studies/{study_uid}/series/{series_uid}/instances")
@router.get("/studies/{study_uid}/series/{series_uid}/instances/metadata")
async def get_all_instances(study_uid: str, series_uid: str):
    return await InstanceDAO.get_all_instances(study_uid, series_uid)

@router.get("/studies/{study_uid}/series/{series_uid}/instances/{instance_uid}")
@router.get("/studies/{study_uid}/series/{series_uid}/instances/{instance_uid}/metadata")
async def get_instance(study_uid: str, series_uid: str, instance_uid: str):
    return await InstanceDAO.get_instance(study_uid, series_uid, instance_uid)

# @router.get("/studies/{study_uid}/series/{series_uid}/instances/{instance_uid}/frames/1")



@router.get("/instances", summary="Get all available instances on server")
async def get_instances():
    arr = [instance for instance in instances if instance["0020000E"]["Value"][0] == "1.2.392.200036.9116.2.6.1.48.1214243055.1484544554.762425"];
    return arr


@router.get("/instances/{instance_uid}/frames/1", summary="Get all available studies on server")
async def get_instance_by_uid(instance_uid: str):
    m = MultipartEncoder(
        fields={"" : ('', instancesPixelData[instance_uid], "image/jls;transfer-syntax=1.2.840.10008.1.2.4.80")}
    )
    return Response(
        m.to_string(),
        media_type="multipart/related"
    )


