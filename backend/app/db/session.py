"""Motores y sesiones SQLAlchemy (async para FastAPI, sync para Alembic)."""

from collections.abc import AsyncIterator

from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings

# FastAPI, WebSockets y el agente usan I/O no bloqueante.
async_engine = create_async_engine(
    settings.get_async_db_url(),
    echo=False,
    future=True,
    pool_pre_ping=True,
)

AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

# Alembic y scripts síncronos.
sync_engine = create_engine(
    settings.get_sync_db_url(),
    echo=False,
    pool_pre_ping=True,
)

SyncSessionLocal = sessionmaker(
    bind=sync_engine,
    autocommit=False,
    autoflush=False,
)


async def get_async_db() -> AsyncIterator[AsyncSession]:
    """Dependencia FastAPI: abre una sesión async y la cierra al terminar."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
