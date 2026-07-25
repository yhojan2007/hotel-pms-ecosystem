from pydantic import BaseModel, ConfigDict, Field
from typing import Optional
from datetime import datetime
from app.models.room import RoomStatus, RoomType

class RoomBase(BaseModel):
    nombre: str = Field(..., example="Habitación 101")
    tipo: RoomType = Field(default=RoomType.INDIVIDUAL, example=RoomType.INDIVIDUAL)
    precio_base: float = Field(..., gt=0, example=50.00)
    estado: RoomStatus = Field(default=RoomStatus.DISPONIBLE, example=RoomStatus.DISPONIBLE)

class RoomCreate(RoomBase):
    pass

class RoomUpdate(BaseModel):
    nombre: Optional[str] = None
    tipo: Optional[RoomType] = None
    precio_base: Optional[float] = None
    estado: Optional[RoomStatus] = None

class RoomStatusUpdate(BaseModel):
    estado: RoomStatus = Field(..., example=RoomStatus.PENDIENTE)

class RoomResponse(RoomBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
