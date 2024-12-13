from fastapi import APIRouter, Depends, HTTPException
from app.users.jwt.current_user import get_current_user_from_access
from app.users.models import UserRole
from app.edit.schemas import (
    EditPatientData, EditDicomFileData,
    PatientInfo, DicomFileInfo
)
from app.edit.dao import EditDAO

router = APIRouter(prefix="/edit", tags=["Edit"])

@router.get("/patient/{patient_id}", response_model=PatientInfo)
async def get_patient_info(
    patient_id: int,
    user_data = Depends(get_current_user_from_access)
):
    """Получение информации о пациенте для редактирования"""
    if user_data.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=403,
            detail="Only administrators can view patient data"
        )

    patient = await EditDAO.get_patient(patient_id)
    if not patient:
        raise HTTPException(
            status_code=404,
            detail="Patient not found"
        )

    return PatientInfo(
        id=patient.id,
        name=patient.name,
        birth_date=patient.birth_date
    )

@router.put("/patient")
async def edit_patient(
    edit_data: EditPatientData,
    user_data = Depends(get_current_user_from_access)
):
    """Редактирование данных пациента"""
    if user_data.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=403,
            detail="Only administrators can edit patient data"
        )

    success = await EditDAO.update_patient(
        patient_id=edit_data.patient_id,
        name=edit_data.name,
        birth_date=edit_data.birth_date
    )

    if not success:
        raise HTTPException(
            status_code=404,
            detail="Patient not found or no changes were made"
        )

    return {"message": "Patient data updated successfully"}

@router.get("/dicom-file/{file_id}", response_model=DicomFileInfo)
async def get_dicom_file_info(
    file_id: int,
    user_data = Depends(get_current_user_from_access)
):
    """Получение информации о DICOM файле для редактирования"""
    if user_data.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=403,
            detail="Only administrators can view DICOM file data"
        )

    dicom_file = await EditDAO.get_dicom_file(file_id)
    if not dicom_file:
        raise HTTPException(
            status_code=404,
            detail="DICOM file not found"
        )

    return DicomFileInfo(
        id=dicom_file.id,
        file_name=dicom_file.file_name,
        upload_date=dicom_file.upload_date,
        upload_time=dicom_file.upload_time if hasattr(dicom_file, 'upload_time') else None,
        uploader_id=dicom_file.uploader_id
    )

@router.put("/dicom-file")
async def edit_dicom_file(
    edit_data: EditDicomFileData,
    user_data = Depends(get_current_user_from_access)
):
    """Редактирование данных DICOM файла"""
    if user_data.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=403,
            detail="Only administrators can edit DICOM file data"
        )

    success = await EditDAO.update_dicom_file(
        file_id=edit_data.file_id,
        file_name=edit_data.file_name,
        upload_date=edit_data.upload_date,
        uploader_id=edit_data.uploader_id
    )

    if not success:
        raise HTTPException(
            status_code=404,
            detail="DICOM file not found or no changes were made"
        )

    return {"message": "DICOM file data updated successfully"}