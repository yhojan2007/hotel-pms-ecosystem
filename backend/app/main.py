from fastapi import Depends, FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.config import settings
from app.api.router import api_router
from app.api.ws import manager
from app.db.session import get_async_db

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# Configuración CORS para permitir conexiones desde el frontend de Next.js
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.get_cors_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir Rutas REST API v1
app.include_router(api_router, prefix=settings.API_V1_STR)

# Endpoint WebSocket para transmisión en tiempo real de estados de habitación
@app.websocket("/ws/rooms")
async def websocket_rooms_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # Mantiene viva la conexión WebSocket escuchando mensajes entrantes del cliente si aplica
            data = await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)

@app.get("/")
def read_root():
    return {
        "status": "ok",
        "service": settings.PROJECT_NAME,
        "docs": "/docs",
        "ws_rooms": "/ws/rooms"
    }

@app.get("/health")
async def health_check(db: AsyncSession = Depends(get_async_db)):
    await db.execute(text("SELECT 1"))
    return {
        "status": "healthy",
        "database": "connected",
        "environment": settings.ENVIRONMENT
    }
