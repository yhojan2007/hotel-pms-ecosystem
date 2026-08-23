"""Configuración de la aplicación cargada desde variables de entorno / ``.env``."""

from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Ajustes tipados del backend.

    Los valores se leen de variables de entorno (Compose las inyecta).
    Campos extra en ``.env`` se ignoran para no romper el arranque.
    """

    PROJECT_NAME: str = "Hotel PMS Ecosystem"
    API_V1_STR: str = "/api/v1"
    ENVIRONMENT: str = "production"
    SECRET_KEY: str = "change_this_secret_key_for_production_demo"
    CORS_ORIGINS: str = "http://localhost:3000"
    BACKEND_PUBLIC_URL: str = "http://localhost:8000"

    # PostgreSQL (host ``db`` es el nombre del servicio en docker-compose)
    POSTGRES_SERVER: str = "db"
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str = "pms_user"
    POSTGRES_PASSWORD: str = "pms_password_secret"
    POSTGRES_DB: str = "hotel_pms_db"

    DATABASE_URL: Optional[str] = None
    SYNC_DATABASE_URL: Optional[str] = None

    # Integraciones opcionales (demo funciona sin claves reales)
    ANTHROPIC_API_KEY: Optional[str] = None
    OPENAI_API_KEY: Optional[str] = None
    ZAVUDEV_API_KEY: Optional[str] = None
    ZAVU_API_KEY: Optional[str] = None
    ZAVU_PHONE_NUMBER_ID: Optional[str] = None
    PAYMENT_WEBHOOK_SECRET: Optional[str] = None

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    def get_async_db_url(self) -> str:
        """URL SQLAlchemy async (driver ``asyncpg``) para FastAPI."""
        if self.DATABASE_URL:
            return self.DATABASE_URL
        return (
            f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    def get_sync_db_url(self) -> str:
        """URL SQLAlchemy síncrona (driver ``psycopg``) para Alembic."""
        if self.SYNC_DATABASE_URL:
            return self.SYNC_DATABASE_URL
        return (
            f"postgresql+psycopg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    def get_cors_origins(self) -> list[str]:
        """Orígenes CORS permitidos, separados por coma en ``CORS_ORIGINS``."""
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]


settings = Settings()
