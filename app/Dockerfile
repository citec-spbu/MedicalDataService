FROM python:3.12-slim

RUN mkdir certs && \
    openssl genrsa -out certs/jwt-private.pem 2048 && \
    openssl rsa -in certs/jwt-private.pem -outform PEM -pubout -out certs/jwt-public.pem

COPY . /app
WORKDIR /app

RUN mv alembic.ini .. && apt-get update && \
    apt-get install -y --no-install-recommends \
    openssl && \
    rm -rf /var/lib/apt/lists/* && pip install \
    --no-cache-dir -r requirements.txt

WORKDIR /



