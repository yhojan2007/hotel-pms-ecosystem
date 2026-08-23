"""Contratos Pydantic de pagos."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from app.models.payment import PaymentStatus


class PaymentBase(BaseModel):
    """Datos de cobro enviados por la API o un webhook."""

    booking_id: int = Field(..., example=1)
    monto: float = Field(..., gt=0, example=200.00)
    proveedor: str = Field(default="mock_gateway", example="stripe")
    referencia_externa: Optional[str] = Field(default=None, example="pi_123456789")


class PaymentCreate(PaymentBase):
    """Registro de un pago nuevo."""

    pass


class PaymentResponse(PaymentBase):
    """Pago persistido, incluyendo estado y timestamps."""

    id: int
    estado: PaymentStatus
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
