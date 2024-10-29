import os
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR: str = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class DBSettings(BaseSettings):
    DB_HOST: str
    DB_PORT: int
    DB_NAME: str
    DB_USER: str
    DB_PASSWORD: str

    model_config = SettingsConfigDict(
        env_file=os.path.join(BASE_DIR, ".env")
    )


class JWTSettings(BaseSettings):
    private_key: str = open(os.path.join(
        BASE_DIR, "certs", "jwt-private.pem"), 'r').read()
    public_key: str = open(os.path.join(
        BASE_DIR, "certs", "jwt-public.pem"), 'r').read()
    algorithm: str = "RS256"
    access_token_expire_minutes: int = 15
    refresh_token_exprire_days: int = 30
    # access_token_expire_minutes: int = 3


db_settings = DBSettings()
jwt_settings = JWTSettings()


def get_db_url() -> str:
    return (f"postgresql+asyncpg://{db_settings.DB_USER}:"
            f"{db_settings.DB_PASSWORD}@{db_settings.DB_HOST}:"
            f"{db_settings.DB_PORT}/{db_settings.DB_NAME}")
