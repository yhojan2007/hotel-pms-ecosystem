"""Casos de uso de reservas y disponibilidad por solapamiento de fechas."""

from datetime import date
from typing import List, Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from app.models.booking import Booking, BookingStatus
from app.models.guest import Guest
from app.models.room import Room, RoomStatus
from app.schemas.booking import BookingCreate
from app.services.room_service import update_room_status


async def get_all_bookings(db: AsyncSession) -> List[Booking]:
    """Lista reservas con habitación y huésped eager-loaded."""
    result = await db.execute(
        select(Booking)
        .options(selectinload(Booking.room), selectinload(Booking.guest))
        .order_by(Booking.id.desc())
    )
    return list(result.scalars().all())


async def get_booking_by_id(db: AsyncSession, booking_id: int) -> Optional[Booking]:
    """Obtiene una reserva por ID con relaciones cargadas."""
    result = await db.execute(
        select(Booking)
        .options(selectinload(Booking.room), selectinload(Booking.guest))
        .filter(Booking.id == booking_id)
    )
    return result.scalars().first()


async def get_latest_pending_booking(db: AsyncSession) -> Optional[Booking]:
    """Última reserva en estado pendiente (atajo del webhook mock)."""
    result = await db.execute(
        select(Booking)
        .options(selectinload(Booking.room), selectinload(Booking.guest))
        .filter(Booking.estado == BookingStatus.PENDIENTE)
        .order_by(Booking.id.desc())
        .limit(1)
    )
    return result.scalars().first()


async def check_room_availability(db: AsyncSession, room_id: int, checkin: date, checkout: date) -> bool:
    """True si no hay reservas pendientes/confirmadas que se solapen con el intervalo."""
    result = await db.execute(
        select(Booking).filter(
            Booking.room_id == room_id,
            Booking.estado.in_([BookingStatus.PENDIENTE, BookingStatus.CONFIRMADA]),
            Booking.fecha_checkin < checkout,
            Booking.fecha_checkout > checkin,
        )
    )
    overlapping_booking = result.scalars().first()
    return overlapping_booking is None


async def create_booking(db: AsyncSession, booking_in: BookingCreate) -> Booking:
    """Crea una pre-reserva y marca la habitación como pendiente (amarillo)."""
    if booking_in.fecha_checkout <= booking_in.fecha_checkin:
        raise ValueError("La fecha de check-out debe ser posterior a la fecha de check-in.")

    room_result = await db.execute(select(Room).filter(Room.id == booking_in.room_id))
    room = room_result.scalars().first()
    if not room:
        raise ValueError(f"La habitación ID {booking_in.room_id} no existe.")

    guest_result = await db.execute(select(Guest).filter(Guest.id == booking_in.guest_id))
    guest = guest_result.scalars().first()
    if not guest:
        raise ValueError(f"El huésped ID {booking_in.guest_id} no existe.")

    is_available = await check_room_availability(
        db, booking_in.room_id, booking_in.fecha_checkin, booking_in.fecha_checkout
    )
    if not is_available:
        raise ValueError(
            f"La habitación ID {booking_in.room_id} ya no está disponible para las fechas seleccionadas."
        )

    booking = Booking(
        room_id=booking_in.room_id,
        guest_id=booking_in.guest_id,
        fecha_checkin=booking_in.fecha_checkin,
        fecha_checkout=booking_in.fecha_checkout,
        estado=BookingStatus.PENDIENTE,
        monto=booking_in.monto,
        referencia_pago=booking_in.referencia_pago,
    )
    db.add(booking)
    await db.commit()
    await db.refresh(booking)

    await update_room_status(db, booking_in.room_id, RoomStatus.PENDIENTE)

    return await get_booking_by_id(db, booking.id)


async def update_booking_status(
    db: AsyncSession,
    booking_id: int,
    new_status: BookingStatus,
    referencia_pago: Optional[str] = None,
) -> Optional[Booking]:
    """Cambia el estado de la reserva y sincroniza el color de la habitación."""
    booking = await get_booking_by_id(db, booking_id)
    if not booking:
        return None

    booking.estado = new_status
    if referencia_pago:
        booking.referencia_pago = referencia_pago

    await db.commit()
    await db.refresh(booking)

    if new_status == BookingStatus.CONFIRMADA:
        await update_room_status(db, booking.room_id, RoomStatus.OCUPADA)
    elif new_status == BookingStatus.CANCELADA or new_status == BookingStatus.COMPLETADA:
        await update_room_status(db, booking.room_id, RoomStatus.DISPONIBLE)

    return booking
