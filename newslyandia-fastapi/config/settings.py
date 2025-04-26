import os

from dotenv import load_dotenv
from pydantic_settings import BaseSettings

env_file = os.getenv("ENV_FILE", ".local.env")
load_dotenv(env_file)


class Settings(BaseSettings):
    DB_HOST: str = ""
    DB_PORT: int = 5432
    DB_USER: str = ""
    DB_PASSWORD: str = ""
    DB_DRIVER: str = "postgresql+asyncpg"
    ECHO: bool = False

    @property
    def db_url(self) -> str:
        return f"{self.DB_DRIVER}://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/"


app_settings = Settings()
