"""Contratos Pydantic de reservas."""

from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from app.models.booking import BookingStatus
from app.schemas.guest import GuestResponse
from app.schemas.room import RoomResponse


class BookingBase(BaseModel):
    """Datos mínimos de una reserva."""

    room_id: int = Field(..., example=1)
    guest_id: int = Field(..., example=1)
    fecha_checkin: date = Field(..., example="2026-08-01")
    fecha_checkout: date = Field(..., example="2026-08-05")
    monto: float = Field(..., gt=0, example=200.00)


class BookingCreate(BookingBase):
    """Alta de reserva; la referencia de pago es opcional."""

    referencia_pago: Optional[str] = None


class BookingStatusUpdate(BaseModel):
    """Cambio de estado de reserva (confirmada, cancelada, etc.)."""

    estado: BookingStatus = Field(..., example=BookingStatus.CONFIRMADA)
    referencia_pago: Optional[str] = None


class BookingResponse(BookingBase):
    """Reserva serializada, opcionalmente con habitación y huésped anidados."""

    id: int
    estado: BookingStatus
    referencia_pago: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    room: Optional[RoomResponse] = None
    guest: Optional[GuestResponse] = None

    model_config = ConfigDict(from_attributes=True)
