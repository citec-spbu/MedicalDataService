from app.dao.base import BaseDAO
from app.dicom_file.models import DicomFile


class DicomDao(BaseDAO):
    model = DicomFile
