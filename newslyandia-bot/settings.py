import os

from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    API_ID: int = 1
    API_HASH: str = ''
    BOT_TOKEN: str = ''
    CHANNEL_ID: int = 1
    GROUP_CHAT_ID: int = 1

    API_URL: str = "http://localhost:8000/api/v1"

    model_config = SettingsConfigDict(
        env_file=os.getenv("ENV_FILE", ".env"),
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

settings = Settings()
