from pydantic import BaseModel, ConfigDict, Field
from typing import Optional
from datetime import datetime
from app.models.payment import PaymentStatus

class PaymentBase(BaseModel):
    booking_id: int = Field(..., example=1)
    monto: float = Field(..., gt=0, example=200.00)
    proveedor: str = Field(default="mock_gateway", example="stripe")
    referencia_externa: Optional[str] = Field(default=None, example="pi_123456789")

class PaymentCreate(PaymentBase):
    pass

class PaymentResponse(PaymentBase):
    id: int
    estado: PaymentStatus
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
