from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path

# Resolve .env path relative to this file's location
ENV_PATH = Path(__file__).parent.parent.parent / ".env"

class Settings(BaseSettings):
    # Server configuration
    host: str
    port: int
    log_level: str

    # API configuration
    api_key: str
    device_timeout_seconds: int

    # Firebase configuration
    firebase_project_id: str
    firebase_service_account_path: str
    firebase_database_url: str

    model_config = SettingsConfigDict(
        env_file=str(ENV_PATH),
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()