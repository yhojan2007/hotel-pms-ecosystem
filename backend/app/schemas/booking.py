from pydantic import BaseModel, ConfigDict, Field
from typing import Optional
from datetime import date, datetime
from app.models.booking import BookingStatus
from app.schemas.room import RoomResponse
from app.schemas.guest import GuestResponse

class BookingBase(BaseModel):
    room_id: int = Field(..., example=1)
    guest_id: int = Field(..., example=1)
    fecha_checkin: date = Field(..., example="2026-08-01")
    fecha_checkout: date = Field(..., example="2026-08-05")
    monto: float = Field(..., gt=0, example=200.00)

class BookingCreate(BookingBase):
    referencia_pago: Optional[str] = None

class BookingStatusUpdate(BaseModel):
    estado: BookingStatus = Field(..., example=BookingStatus.CONFIRMADA)
    referencia_pago: Optional[str] = None

class BookingResponse(BookingBase):
    id: int
    estado: BookingStatus
    referencia_pago: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    room: Optional[RoomResponse] = None
    guest: Optional[GuestResponse] = None

    model_config = ConfigDict(from_attributes=True)
