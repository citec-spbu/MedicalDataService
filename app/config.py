import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from minio import Minio

BASE_DIR: str = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class DBSettings(BaseSettings):
    DB_HOST: str
    DB_PORT: int
    DB_NAME: str
    DB_USER: str
    DB_PASSWORD: str

    model_config = SettingsConfigDict(
        env_file=os.path.join(BASE_DIR, ".env"),
        extra="allow"
    )


class JWTSettings(BaseSettings):
    private_key: str = open(os.path.join(
        BASE_DIR, "certs", "jwt-private.pem"), 'r').read()
    public_key: str = open(os.path.join(
        BASE_DIR, "certs", "jwt-public.pem"), 'r').read()
    algorithm: str = "RS256"
    access_token_expire_minutes: int = 15
    refresh_token_exprire_days: int = 30


class MinioSettings(BaseSettings):
    MINIO_HOST: str
    MINIO_PORT: int
    MINIO_ACCESS_KEY: str
    MINIO_SECRET_KEY: str
    MINIO_BUCKET: str
    MINIO_LOCAL_DOWNLOAD_PATH: str

    model_config = SettingsConfigDict(
        env_file=os.path.join(BASE_DIR, ".env"),
        extra="allow"
    )

    def get_client(self) -> Minio:
        return Minio(
            f"{self.MINIO_HOST}:{self.MINIO_PORT}",
            access_key=self.MINIO_ACCESS_KEY,
            secret_key=self.MINIO_SECRET_KEY,
            secure=False
        )

class RabbitMQSettings(BaseSettings):
    RABBITMQ_HOST: str
    RABBITMQ_PORT: int
    RABBITMQ_USER: str
    RABBITMQ_PASSWORD: str

    model_config = SettingsConfigDict(
        env_file=os.path.join(BASE_DIR, ".env"),
        extra = "allow"
    )

    @property
    def url(self) -> str:
        return f"amqp://{self.RABBITMQ_USER}:{self.RABBITMQ_PASSWORD}@{self.RABBITMQ_HOST}:{self.RABBITMQ_PORT}/"

db_settings = DBSettings()
jwt_settings = JWTSettings()
minio_settings = MinioSettings()
rabbitmq_settings = RabbitMQSettings()

def get_db_url() -> str:
    return (f"postgresql+asyncpg://{db_settings.DB_USER}:"
            f"{db_settings.DB_PASSWORD}@{db_settings.DB_HOST}:"
            f"{db_settings.DB_PORT}/{db_settings.DB_NAME}")


def get_minio_client() -> Minio:
    return minio_settings.get_client()