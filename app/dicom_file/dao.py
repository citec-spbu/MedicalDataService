from app.dao.base import BaseDAO
from app.dicom_file.models import DicomFile

class DicomFileDAO(BaseDAO):
    model = DicomFile