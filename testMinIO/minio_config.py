from minio import Minio

minio_client = Minio(
    "localhost:9000",
    access_key="admin",
    secret_key="password",
    secure=False  #True, если используется HTTPS
)
