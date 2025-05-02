import os

from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    API_URL: str = "http://localhost:8000/api/v1"
    NEWS_LINK: str = ""
    OLLAMA_URL: str = ""

    model_config = SettingsConfigDict(
        env_file=os.getenv("ENV_FILE", ".env"),
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

settings = Settings()
