from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# Configuración CORS para permitir conexiones desde el frontend de Next.js
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {
        "status": "ok",
        "service": settings.PROJECT_NAME,
        "docs": "/docs"
    }

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "database": "connected"
    }
