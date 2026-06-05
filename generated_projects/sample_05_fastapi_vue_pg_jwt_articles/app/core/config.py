import os
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    CORS_ORIGINS: str = "*"
    APP_NAME: str = "FastAPI Vue App"
    ENVIRONMENT: str = "development"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

    @property
    def CORS_ORIGINS_LIST(self) -> list:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]

settings = Settings()