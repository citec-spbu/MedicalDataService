from fastapi import APIRouter, UploadFile, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from app.dao.base import BaseDAO
from app.dicom_file.models import DicomFile
from app.config import get_minio_client, rabbitmq_settings, minio_settings
from app.users.jwt.current_user import get_current_user_from_access
from app.users.models import User, UserRole
from app.users.dao import UserDAO
from app.users.schemas import SUser, SUserWithRole
from app.broker import router as broker_router
from app.broker import IndexQuery
from app.deferred_operations.models import DeferredOperation, RequestType
import hashlib
import io
import zipfile
import pydicom
from datetime import datetime
from sqlalchemy import select, update
from app.database import async_session_maker

router = APIRouter(prefix="/upload", tags=["Upload"])

MINIO_BUCKET = minio_settings.MINIO_BUCKET


async def is_dicom_file(file_bytes: bytes) -> bool:
    try:
        dataset = pydicom.dcmread(io.BytesIO(file_bytes))
        return True
    except:
        return False


async def calculate_hash(file_bytes: bytes) -> str:
    return hashlib.sha256(file_bytes).hexdigest()


async def check_duplicate_hash(file_hash: str) -> bool:
    async with async_session_maker() as session:
        query = select(DicomFile).where(DicomFile.file_hash == file_hash)
        result = await session.execute(query)
        return result.scalar_one_or_none() is not None

@router.post("/")
async def upload_dicom_archive(
        file: UploadFile,
        user_data: SUserWithRole = Depends(get_current_user_from_access)
):
    # проверка роли
    if user_data.role == UserRole.TECHNICAL:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient access rights"
        )

    try:
        user_id = await UserDAO.get_user_id_by_nickname(user_data.nickname)

        if not file.filename.endswith('.zip'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only ZIP archives are allowed"
            )

        # запись об операции загрузки
        async with async_session_maker() as session:
            deferred_operation = DeferredOperation(
                requester_id=user_id,
                loading_state=0.0,
                request_type=RequestType.UPLOADING
            )
            session.add(deferred_operation)
            await session.commit()
            operation_id = deferred_operation.id


        # читаем файл в озу
        zip_content = await file.read()
        zip_hash = await calculate_hash(zip_content)

        # проверка на дубли
        if await check_duplicate_hash(zip_hash):
            raise HTTPException(
                status_code=400,
                detail="This file has already been uploaded"
            )

        # объект архива
        zip_buffer = io.BytesIO(zip_content)
        minio_client = get_minio_client()

        if not minio_client.bucket_exists(MINIO_BUCKET):
            minio_client.make_bucket(MINIO_BUCKET)

        # валидация содержимого
        with zipfile.ZipFile(zip_buffer, 'r') as zip_ref:

            dicom_files = []
            for file_info in zip_ref.filelist:
                if file_info.filename.endswith('/'):
                    continue

                file_content = zip_ref.read(file_info.filename)
                if not await is_dicom_file(file_content):
                    raise HTTPException(
                        status_code=400,
                        detail=f"File {file_info.filename} is not a valid DICOM file"
                    )
                dicom_files.append((file_info.filename, file_content))

            if not dicom_files:
                raise HTTPException(
                    status_code=400,
                    detail="No DICOM files found in the archive"
                )

        # статус загрузки после валидации (50%)
        async with async_session_maker() as session:
            await session.execute(
                update(DeferredOperation)
                .where(DeferredOperation.id == operation_id)
                .values(loading_state=0.5)
            )
            await session.commit()

        # загрузка в MinIO
        zip_buffer.seek(0)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        minio_path = f"archives/{user_id}/{timestamp}_{file.filename}"

        try:
            minio_client.put_object(
                MINIO_BUCKET,
                minio_path,
                zip_buffer,
                length=len(zip_content),
                content_type='application/zip'
            )
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to upload to MinIO: {str(e)}"
            )

        # статус после загрузки в MinIO (75%)
        async with async_session_maker() as session:
            await session.execute(
                update(DeferredOperation)
                .where(DeferredOperation.id == operation_id)
                .values(loading_state=0.75)
            )
            await session.commit()

        # сохранение информации в бд
        async with async_session_maker() as session:
            dicom_file = DicomFile(
                uploader_id=user_id,
                file_name=file.filename,
                minio_path=minio_path,
                file_hash=zip_hash
            )
            session.add(dicom_file)

            # статус после сохранения в БД (90%)
            await session.execute(
                update(DeferredOperation)
                .where(DeferredOperation.id == operation_id)
                .values(loading_state=0.9)
            )

            await session.commit()

        # отправка в очередь RabbitMQ
        try:
            await broker_router.broker.publish(
                message=IndexQuery(
                    user_id=user_id,
                    bucket_name=MINIO_BUCKET,
                    minio_path=minio_path
                ),
                queue="dicom_processing"
            )

            # статус после отправки в RabbitMQ (100%)
            async with async_session_maker() as session:
                await session.execute(
                    update(DeferredOperation)
                    .where(DeferredOperation.id == operation_id)
                    .values(loading_state=1.0)
                )
                await session.commit()

        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to send message to RabbitMQ: {str(e)}"
            )

        return {
            "message": "Upload successful"
        }

    except HTTPException:
        raise
    except Exception as e:
        if 'operation_id' in locals():
            async with async_session_maker() as session:
                await session.execute(
                    update(DeferredOperation)
                    .where(DeferredOperation.id == operation_id)
                    .values(loading_state=-1.0)
                )
                await session.commit()

        raise HTTPException(status_code=500, detail=str(e))
