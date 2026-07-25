from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    PROJECT_NAME: str = "Hotel PMS Ecosystem"
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = "change_this_secret_key_for_production_demo"
    
    # Configuración Base de Datos
    POSTGRES_SERVER: str = "db"
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str = "pms_user"
    POSTGRES_PASSWORD: str = "pms_password_secret"
    POSTGRES_DB: str = "hotel_pms_db"
    
    DATABASE_URL: Optional[str] = None
    SYNC_DATABASE_URL: Optional[str] = None
    
    # Integraciones futuras (Fases 3 y 5)
    ANTHROPIC_API_KEY: Optional[str] = None
    ZAVU_API_KEY: Optional[str] = None
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    def get_async_db_url(self) -> str:
        if self.DATABASE_URL:
            return self.DATABASE_URL
        return f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

    def get_sync_db_url(self) -> str:
        if self.SYNC_DATABASE_URL:
            return self.SYNC_DATABASE_URL
        return f"postgresql+psycopg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

settings = Settings()
