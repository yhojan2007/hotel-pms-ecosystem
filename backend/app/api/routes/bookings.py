"""Rutas REST de reservas."""

from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_async_db
from app.schemas.booking import BookingCreate, BookingResponse, BookingStatusUpdate
from app.services import booking_service

router = APIRouter(prefix="/bookings", tags=["Reservas"])


@router.get("", response_model=List[BookingResponse])
async def list_bookings(db: AsyncSession = Depends(get_async_db)) -> List[BookingResponse]:
    """Lista reservas con habitación y huésped cargados."""
    return await booking_service.get_all_bookings(db)


@router.get("/{booking_id}", response_model=BookingResponse)
async def get_booking(booking_id: int, db: AsyncSession = Depends(get_async_db)) -> BookingResponse:
    """Devuelve una reserva por ID o 404."""
    booking = await booking_service.get_booking_by_id(db, booking_id)
    if not booking:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Reserva no encontrada")
    return booking


@router.post("", response_model=BookingResponse, status_code=status.HTTP_201_CREATED)
async def create_booking(
    booking_in: BookingCreate, db: AsyncSession = Depends(get_async_db)
) -> BookingResponse:
    """Crea una reserva, marca la habitación como pendiente y notifica al PMS."""
    try:
        return await booking_service.create_booking(db, booking_in)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.patch("/{booking_id}/status", response_model=BookingResponse)
async def update_booking_status(
    booking_id: int, update_in: BookingStatusUpdate, db: AsyncSession = Depends(get_async_db)
) -> BookingResponse:
    """Actualiza el estado de la reserva y sincroniza el color de la habitación."""
    updated_booking = await booking_service.update_booking_status(
        db, booking_id, update_in.estado, update_in.referencia_pago
    )
    if not updated_booking:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Reserva no encontrada")
    return updated_booking
