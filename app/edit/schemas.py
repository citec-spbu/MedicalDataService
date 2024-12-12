from pydantic import BaseModel, Field
from datetime import date, time
from typing import Optional

class PatientInfo(BaseModel):
    id: int
    name: str
    birth_date: Optional[date] = None

class EditPatientData(BaseModel):
    patient_id: int
    name: Optional[str] = Field(None, min_length=3, max_length=100)
    birth_date: Optional[date] = None

class DicomFileInfo(BaseModel):
    id: int
    file_name: str
    upload_date: date
    upload_time: time
    uploader_id: int

class EditDicomFileData(BaseModel):
    file_id: int
    file_name: Optional[str] = Field(None, min_length=1, max_length=255)
    upload_date: Optional[date] = None
    upload_time: Optional[time] = None
    uploader_id: Optional[int] = None 