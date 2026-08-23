"""Esquemas Pydantic de entrada/salida de la API (separados de los modelos ORM)."""

from app.schemas.booking import BookingCreate, BookingResponse, BookingStatusUpdate
from app.schemas.guest import GuestCreate, GuestResponse, GuestUpdate
from app.schemas.payment import PaymentCreate, PaymentResponse
from app.schemas.room import RoomCreate, RoomResponse, RoomStatusUpdate, RoomUpdate

__all__ = [
    "RoomCreate",
    "RoomUpdate",
    "RoomStatusUpdate",
    "RoomResponse",
    "GuestCreate",
    "GuestUpdate",
    "GuestResponse",
    "BookingCreate",
    "BookingStatusUpdate",
    "BookingResponse",
    "PaymentCreate",
    "PaymentResponse",
]
