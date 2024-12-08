from pydicom import FileDataset
from app.patients.dao import PatientDAO


async def index_patient(ds: FileDataset):
    if "ImageType" in ds:
        patient_id: int | None = None
        patient_name: str = "DEFAULT NAME"
        patient_sex: str = '?'
        if "PatientID" in ds:
            patient_id = int(ds.PatientID)
        if "PatientName" in ds and str(ds.PatientName) != "":
            patient_name = str(ds.PatientName)
        if "PatientSex" in ds and str(ds.PatientSex) != "":
            patient_sex = str(ds.PatientSex)
        patient = await PatientDAO.find_one_or_none(
            id=patient_id
        )
        if patient is None:
            query = {"name": patient_name,
                     "sex": patient_sex}
            if patient_id is not None:
                query.update(id=patient_id)
            return await PatientDAO.add(**query)
        return patient
