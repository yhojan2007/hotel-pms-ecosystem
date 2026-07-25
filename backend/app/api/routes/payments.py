from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.db.session import get_async_db
from app.schemas.payment import PaymentCreate, PaymentResponse
from app.services import payment_service

router = APIRouter(prefix="/payments", tags=["Pagos"])

@router.post("", response_model=PaymentResponse, status_code=status.HTTP_201_CREATED)
async def process_payment(payment_in: PaymentCreate, db: AsyncSession = Depends(get_async_db)):
    """
    Registra un pago y confirma la reserva asociada.
    Actualiza la habitación a 'ocupada' (Rojo) y emite evento WebSocket en tiempo real.
    """
    return await payment_service.record_payment(db, payment_in, is_confirmed=True)

@router.get("/booking/{booking_id}", response_model=List[PaymentResponse])
async def get_booking_payments(booking_id: int, db: AsyncSession = Depends(get_async_db)):
    """Obtiene el historial de pagos asociados a una reserva."""
    return await payment_service.get_payments_by_booking(db, booking_id)
