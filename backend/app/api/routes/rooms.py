"""Rutas REST de habitaciones."""

from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_async_db
from app.schemas.room import RoomCreate, RoomResponse, RoomStatusUpdate
from app.services import room_service

router = APIRouter(prefix="/rooms", tags=["Habitaciones"])


@router.get("", response_model=List[RoomResponse])
async def list_rooms(db: AsyncSession = Depends(get_async_db)) -> List[RoomResponse]:
    """Lista todas las habitaciones con su estado actual."""
    return await room_service.get_all_rooms(db)


@router.get("/{room_id}", response_model=RoomResponse)
async def get_room(room_id: int, db: AsyncSession = Depends(get_async_db)) -> RoomResponse:
    """Devuelve una habitación por ID o 404."""
    room = await room_service.get_room_by_id(db, room_id)
    if not room:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Habitación no encontrada")
    return room


@router.post("", response_model=RoomResponse, status_code=status.HTTP_201_CREATED)
async def create_room(room_in: RoomCreate, db: AsyncSession = Depends(get_async_db)) -> RoomResponse:
    """Crea una habitación nueva."""
    return await room_service.create_room(db, room_in)


@router.patch("/{room_id}/status", response_model=RoomResponse)
async def update_room_status(
    room_id: int, status_update: RoomStatusUpdate, db: AsyncSession = Depends(get_async_db)
) -> RoomResponse:
    """Cambia el estado (disponible / pendiente / ocupada) y notifica por WebSocket."""
    updated_room = await room_service.update_room_status(db, room_id, status_update.estado)
    if not updated_room:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Habitación no encontrada")
    return updated_room
