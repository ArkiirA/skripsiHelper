from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    APP_NAME: str = "SkripsiHelper"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = False
    ENV: str = "development"

    DATABASE_URL: str = Field(
        default="postgresql+psycopg2://skripsi:skripsi123@127.0.0.1:5432/skripsi"
    )
    SQL_DEBUG: bool = False

    GCS_BUCKET_NAME: str = "skripsi-helper-uploads"
    GCS_CREDENTIALS_PATH: str | None = None

    CORS_ORIGINS: list[str] = ["http://localhost:3000", "http://localhost:5173"]

    # Midtrans settings
    MIDTRANS_SERVER_KEY: str = Field(default="SB-Mid-server-dummy")
    MIDTRANS_CLIENT_KEY: str = Field(default="SB-Mid-client-dummy")
    MIDTRANS_IS_PRODUCTION: bool = False

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
