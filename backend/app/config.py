"""
Configuracion de la aplicacion
"""
from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Optional, List


class Settings(BaseSettings):
    """Configuracion desde variables de entorno"""

    APP_NAME: str = "QA Guardian"
    APP_VERSION: str = "2.0.0"
    ENVIRONMENT: str = Field(default="development")
    DEBUG: bool = Field(default=False)

    HOST: str = "0.0.0.0"
    PORT: int = 8081

    DATABASE_URL: str = Field(default="postgresql+asyncpg://qa_guardian:dev_password@localhost:5432/qa_guardian")
    REDIS_URL: str = Field(default="redis://localhost:6379/0")

    JWT_SECRET_KEY: str = Field(default="change-this-in-production-min-32-chars!!")
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 15

    CORS_ORIGINS: List[str] = Field(default=["*"])

    RATE_LIMIT_PER_MINUTE: int = 100

    SENTRY_DSN: Optional[str] = None

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
