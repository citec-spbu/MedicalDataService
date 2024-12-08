from pydicom import FileDataset
from app.studies.dao import StudyDAO


async def index_study(ds: FileDataset, patient_id: int):
    if "ImageType" in ds:
        study_id: str = ds.StudyInstanceUID
        study_name: str = "DEFAULT STUDY NAME"
        if "StudyDescription" in ds:
            study_name = str(ds.StudyDescription)
        study = await StudyDAO.find_one_or_none(
            id=study_id
        )
        if study is None:
            query = {"id": study_id,
                     "patient_id": patient_id,
                     "study_name": study_name}
            return await StudyDAO.add(**query)
        return study
