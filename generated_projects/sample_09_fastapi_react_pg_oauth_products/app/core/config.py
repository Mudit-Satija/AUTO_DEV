import os
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    PROJECT_NAME: str = "FastAPI OAuth App"
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-here")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://user:password@localhost/dbname")
    OAUTH_CLIENT_ID: str = os.getenv("OAUTH_CLIENT_ID", "")
    OAUTH_CLIENT_SECRET: str = os.getenv("OAUTH_CLIENT_SECRET", "")
    OAUTH_AUTHORIZATION_URL: str = os.getenv("OAUTH_AUTHORIZATION_URL", "")
    OAUTH_TOKEN_URL: str = os.getenv("OAUTH_TOKEN_URL", "")
    OAUTH_USERINFO_URL: str = os.getenv("OAUTH_USERINFO_URL", "")
    OAUTH_REDIRECT_URI: str = os.getenv("OAUTH_REDIRECT_URI", "")
    OAUTH_SCOPE: str = os.getenv("OAUTH_SCOPE", "openid profile email")
    FRONTEND_URL: str = os.getenv("FRONTEND_URL", "http://localhost:3000")
    CORS_ORIGINS: list = ["http://localhost:3000", "http://localhost:8000"]

    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()