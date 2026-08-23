"""Punto de entrada de la API FastAPI del PMS hotelero.

Expone:
- REST bajo ``/api/v1`` (habitaciones, huéspedes, reservas, pagos, webhooks).
- WebSocket ``/ws/rooms`` para actualizar el dashboard en tiempo real.
- ``/health`` para comprobar conectividad con PostgreSQL.
"""

from typing import Any

from fastapi import Depends, FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.router import api_router
from app.api.ws import manager
from app.core.config import settings
from app.db.session import get_async_db

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
)

# CORS: el dashboard Next.js (localhost:3000 por defecto) consume REST y WS.
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.get_cors_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix=settings.API_V1_STR)


@app.websocket("/ws/rooms")
async def websocket_rooms_endpoint(websocket: WebSocket) -> None:
    """Mantiene abierta una conexión WebSocket para eventos de habitación.

    El servidor no interpreta el texto del cliente; solo lo lee para
    detectar desconexiones (ping implícito / keep-alive).
    """
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)


@app.get("/")
def read_root() -> dict[str, str]:
    """Describe el servicio y enlaces útiles (docs y canal WS)."""
    return {
        "status": "ok",
        "service": settings.PROJECT_NAME,
        "docs": "/docs",
        "ws_rooms": "/ws/rooms",
    }


@app.get("/health")
async def health_check(db: AsyncSession = Depends(get_async_db)) -> dict[str, Any]:
    """Healthcheck liveness + readiness: ejecuta ``SELECT 1`` contra la DB."""
    await db.execute(text("SELECT 1"))
    return {
        "status": "healthy",
        "database": "connected",
        "environment": settings.ENVIRONMENT,
    }
