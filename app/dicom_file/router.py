from zipfile import ZipFile
from io import BytesIO
from fastapi import (
    APIRouter,
    UploadFile,
    File,
    HTTPException,
    Depends,
    status
)
from pydicom import dcmread
from app.broker.router import (
    router as broker_router,
    SqlQuery,
    TableType
)
from app.patients.dao import PatientDAO
from app.users.jwt.current_user import get_current_user_with_role_from_access
from app.users.models import UserRole
from app.users.schemas import SUserWithRole

session_patients: set = set()

router = APIRouter(
    prefix="/dicom",
    tags=["Working with files in DICOM format"]
)


@router.post("/upload", summary="Upload zip file")
async def upload(
    file: UploadFile = File(...),
    user_data: SUserWithRole = Depends(get_current_user_with_role_from_access)
) -> dict:
    if user_data.role == UserRole.TECHNICAL:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Insufficient access rights"
        )
    if file.content_type != "application/zip":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid document type"
        )
    with ZipFile(BytesIO(await file.read())) as zip_file:
        for file_info in zip_file.infolist():
            if not file_info.is_dir():
                ds = dcmread(
                    fp=BytesIO(zip_file.read(file_info.filename)),
                    force=True
                )
                # variable = ds.SeriesDescription
                # variable = ds.StudyDescription
                # print(variable)
                # print(type(variable))
                if "ImageType" in ds:
                    patient_id: int = int(ds.PatientID)
                    # patient_id: int = 98
                    patient_name: str | None = None
                    patient_sex: str | None = None
                    if "PatientName" in ds and str(ds.PatientName) != "":
                        patient_name = str(ds.PatientName)
                    if "PatientSex" in ds and str(ds.PatientSex) != "":
                        patient_sex = str(ds.PatientSex)
                    patient = await PatientDAO.find_one_or_none(
                        id=patient_id
                    )
                    if patient is None and patient_id not in session_patients:
                        session_patients.add(patient_id)
                        await broker_router.broker.publish(
                            message=SqlQuery(
                                table_type=TableType.PATIENTS,
                                value={"id": patient_id,
                                       "name": patient_name,
                                       "sex": patient_sex}
                            ),
                            queue="sql_query"
                        )
    return {"message": f"Successfuly uploaded {file.filename}"}
