1. Установка и запуск MinIO сервера

https://min.io/download?license=agpl&platform=linux

>wget https://dl.min.io/server/minio/release/linux-amd64/minio

>chmod +x minio

>MINIO_ROOT_USER=admin MINIO_ROOT_PASSWORD=password ./minio server data --console-address ":9001"

2. В графическом интерфейсе по адресу http://127.0.0.1:9001/ создаём баккет "data-storage"

3. В файле minio_config.py указываем данные для подключения

4. Запуск

uvicorn main:app --reload

