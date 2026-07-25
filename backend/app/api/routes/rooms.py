from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.db.session import get_async_db
from app.schemas.room import RoomCreate, RoomStatusUpdate, RoomResponse
from app.services import room_service

router = APIRouter(prefix="/rooms", tags=["Habitaciones"])

@router.get("", response_model=List[RoomResponse])
async def list_rooms(db: AsyncSession = Depends(get_async_db)):
    """Obtiene la lista de todas las habitaciones con su estado actual."""
    return await room_service.get_all_rooms(db)

@router.get("/{room_id}", response_model=RoomResponse)
async def get_room(room_id: int, db: AsyncSession = Depends(get_async_db)):
    """Obtiene los detalles de una habitación por su ID."""
    room = await room_service.get_room_by_id(db, room_id)
    if not room:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Habitación no encontrada")
    return room

@router.post("", response_model=RoomResponse, status_code=status.HTTP_201_CREATED)
async def create_room(room_in: RoomCreate, db: AsyncSession = Depends(get_async_db)):
    """Crea una nueva habitación en el sistema."""
    return await room_service.create_room(db, room_in)

@router.patch("/{room_id}/status", response_model=RoomResponse)
async def update_room_status(
    room_id: int, status_update: RoomStatusUpdate, db: AsyncSession = Depends(get_async_db)
):
    """
    Actualiza el estado de una habitación (disponible, pendiente, ocupada).
    Emite automáticamente un evento WebSocket en tiempo real al PMS.
    """
    updated_room = await room_service.update_room_status(db, room_id, status_update.estado)
    if not updated_room:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Habitación no encontrada")
    return updated_room
