"""Contratos Pydantic de habitaciones."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from app.models.room import RoomStatus, RoomType


class RoomBase(BaseModel):
    """Campos compartidos de una habitación."""

    nombre: str = Field(..., example="Habitación 101")
    tipo: RoomType = Field(default=RoomType.INDIVIDUAL, example=RoomType.INDIVIDUAL)
    precio_base: float = Field(..., gt=0, example=50.00)
    estado: RoomStatus = Field(default=RoomStatus.DISPONIBLE, example=RoomStatus.DISPONIBLE)


class RoomCreate(RoomBase):
    """Payload para crear una habitación."""

    pass


class RoomUpdate(BaseModel):
    """Actualización parcial de habitación."""

    nombre: Optional[str] = None
    tipo: Optional[RoomType] = None
    precio_base: Optional[float] = None
    estado: Optional[RoomStatus] = None


class RoomStatusUpdate(BaseModel):
    """Cambio de estado (PATCH ``/rooms/{id}/status``)."""

    estado: RoomStatus = Field(..., example=RoomStatus.PENDIENTE)


class RoomResponse(RoomBase):
    """Habitación serializada hacia el cliente."""

    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
