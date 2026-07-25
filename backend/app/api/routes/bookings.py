from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.db.session import get_async_db
from app.schemas.booking import BookingCreate, BookingStatusUpdate, BookingResponse
from app.services import booking_service

router = APIRouter(prefix="/bookings", tags=["Reservas"])

@router.get("", response_model=List[BookingResponse])
async def list_bookings(db: AsyncSession = Depends(get_async_db)):
    """Obtiene la lista de todas las reservas con sus relaciones de habitación y huésped."""
    return await booking_service.get_all_bookings(db)

@router.get("/{booking_id}", response_model=BookingResponse)
async def get_booking(booking_id: int, db: AsyncSession = Depends(get_async_db)):
    """Obtiene una reserva por su ID."""
    booking = await booking_service.get_booking_by_id(db, booking_id)
    if not booking:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Reserva no encontrada")
    return booking

@router.post("", response_model=BookingResponse, status_code=status.HTTP_201_CREATED)
async def create_booking(booking_in: BookingCreate, db: AsyncSession = Depends(get_async_db)):
    """
    Crea una nueva reserva.
    Cambia automáticamente el estado de la habitación a 'pendiente' (Amarillo)
    y notifica por WebSocket al PMS.
    """
    try:
        return await booking_service.create_booking(db, booking_in)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.patch("/{booking_id}/status", response_model=BookingResponse)
async def update_booking_status(
    booking_id: int, update_in: BookingStatusUpdate, db: AsyncSession = Depends(get_async_db)
):
    """
    Actualiza el estado de una reserva.
    Si se confirma, cambia la habitación a 'ocupada' (Rojo).
    Si se cancela, la habitación vuelve a 'disponible' (Verde).
    """
    updated_booking = await booking_service.update_booking_status(
        db, booking_id, update_in.estado, update_in.referencia_pago
    )
    if not updated_booking:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Reserva no encontrada")
    return updated_booking
