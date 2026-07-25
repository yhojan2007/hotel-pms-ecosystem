from pydantic import BaseModel, ConfigDict, Field
from typing import Optional
from datetime import datetime

class GuestBase(BaseModel):
    nombre: str = Field(..., example="Juan Pérez")
    contacto: str = Field(..., example="+573001234567")

class GuestCreate(GuestBase):
    historial_gasto: Optional[float] = 0.00

class GuestUpdate(BaseModel):
    nombre: Optional[str] = None
    contacto: Optional[str] = None
    historial_gasto: Optional[float] = None

class GuestResponse(GuestBase):
    id: int
    historial_gasto: float
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
