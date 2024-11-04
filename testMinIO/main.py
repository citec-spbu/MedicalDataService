from fastapi import FastAPI, UploadFile, HTTPException, BackgroundTasks
from minio_config import minio_client
import aiofiles
import zipfile
import os
import shutil

app = FastAPI()

async def extract_and_upload(zip_file_path: str, bucket_name: str):
    # временная папка на сервере для распаковки
    extract_dir = "/tmp/extracted/"
    os.makedirs(extract_dir, exist_ok=True)

    full_path = os.path.abspath(zip_file_path)
    print(f"Распаковка: {full_path}")

    # распаковка
    with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
        zip_ref.extractall(extract_dir)

    # загрузка каждого файла в MinIO
    for root, _, files in os.walk(extract_dir):
        for file_name in files:
            full_path = os.path.join(root, file_name)
            relative_path = os.path.relpath(full_path, extract_dir)
            object_name = f"extracted/{relative_path}".replace('\\', '/')
            minio_client.fput_object(bucket_name, object_name, full_path)

    # удаление временного файла
    try:
        os.remove(zip_file_path)
        if os.path.exists(extract_dir):
            shutil.rmtree(extract_dir)
    except Exception as e:
        print(f"Ошибка при удалении временных файлов!!! {str(e)}")

@app.post("/upload/")
async def upload_and_extract(file: UploadFile, background_tasks: BackgroundTasks):
    try:

        temp_dir = "/tmp/uploads/"
        os.makedirs(temp_dir, exist_ok=True)
        zip_file_path = os.path.join(temp_dir, file.filename)

        async with aiofiles.open(zip_file_path, "wb") as out_file:
            content = await file.read()
            await out_file.write(content)

        # задача по распаковке и загрузке распакованных файлов в MinIO
        # "data-storage" - название бакита в MinIO
        background_tasks.add_task(extract_and_upload, zip_file_path, "data-storage")

        return {"message": "File uploaded"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
