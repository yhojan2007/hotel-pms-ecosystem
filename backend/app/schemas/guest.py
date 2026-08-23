"""Contratos Pydantic de huéspedes."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class GuestBase(BaseModel):
    """Nombre y contacto (WhatsApp)."""

    nombre: str = Field(..., example="Juan Pérez")
    contacto: str = Field(..., example="+573001234567")


class GuestCreate(GuestBase):
    """Alta de huésped; ``historial_gasto`` arranca en 0 si se omite."""

    historial_gasto: Optional[float] = 0.00


class GuestUpdate(BaseModel):
    """Actualización parcial de huésped."""

    nombre: Optional[str] = None
    contacto: Optional[str] = None
    historial_gasto: Optional[float] = None


class GuestResponse(GuestBase):
    """Huésped serializado hacia el cliente."""

    id: int
    historial_gasto: float
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
