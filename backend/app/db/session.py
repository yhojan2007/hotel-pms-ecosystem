from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

# Motor Asíncrono para FastAPI / WebSockets / Agente
async_engine = create_async_engine(
    settings.get_async_db_url(),
    echo=False,
    future=True,
    pool_pre_ping=True
)

AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False
)

# Motor Síncrono para Alembic o tareas que requieran sincronía
sync_engine = create_engine(
    settings.get_sync_db_url(),
    echo=False,
    pool_pre_ping=True
)

SyncSessionLocal = sessionmaker(
    bind=sync_engine,
    autocommit=False,
    autoflush=False
)

async def get_async_db():
    """Dependency injection handler para obtener sesiones de base de datos asíncronas en FastAPI."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
