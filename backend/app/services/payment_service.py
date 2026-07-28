from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List, Optional
from app.models.payment import Payment, PaymentStatus
from app.models.booking import BookingStatus
from app.schemas.payment import PaymentCreate
from app.services.booking_service import update_booking_status
from app.services.guest_service import update_guest_spending

async def record_payment(db: AsyncSession, payment_in: PaymentCreate, is_confirmed: bool = True) -> Payment:
    if payment_in.referencia_externa:
        result = await db.execute(
            select(Payment).filter(Payment.referencia_externa == payment_in.referencia_externa)
        )
        existing_payment = result.scalars().first()
        if existing_payment:
            return existing_payment

    status = PaymentStatus.CONFIRMADO if is_confirmed else PaymentStatus.FALLIDO

    payment = Payment(
        booking_id=payment_in.booking_id,
        estado=status,
        monto=payment_in.monto,
        proveedor=payment_in.proveedor,
        referencia_externa=payment_in.referencia_externa
    )
    db.add(payment)
    await db.commit()
    await db.refresh(payment)

    if is_confirmed:
        # 1. Confirmar la reserva (esto pasa la habitación a 'ocupada' y emite por WebSocket)
        booking = await update_booking_status(
            db, payment_in.booking_id, BookingStatus.CONFIRMADA, referencia_pago=payment_in.referencia_externa
        )
        
        # 2. Actualizar el historial de gasto del huésped
        if booking:
            await update_guest_spending(db, booking.guest_id, payment_in.monto)

    return payment

async def get_payments_by_booking(db: AsyncSession, booking_id: int) -> List[Payment]:
    result = await db.execute(select(Payment).filter(Payment.booking_id == booking_id))
    return list(result.scalars().all())
