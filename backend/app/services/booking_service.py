from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from typing import List, Optional
from datetime import date
from app.models.booking import Booking, BookingStatus
from app.models.guest import Guest
from app.models.room import Room, RoomStatus
from app.schemas.booking import BookingCreate
from app.services.room_service import update_room_status

async def get_all_bookings(db: AsyncSession) -> List[Booking]:
    result = await db.execute(
        select(Booking)
        .options(selectinload(Booking.room), selectinload(Booking.guest))
        .order_by(Booking.id.desc())
    )
    return list(result.scalars().all())

async def get_booking_by_id(db: AsyncSession, booking_id: int) -> Optional[Booking]:
    result = await db.execute(
        select(Booking)
        .options(selectinload(Booking.room), selectinload(Booking.guest))
        .filter(Booking.id == booking_id)
    )
    return result.scalars().first()

async def get_latest_pending_booking(db: AsyncSession) -> Optional[Booking]:
    result = await db.execute(
        select(Booking)
        .options(selectinload(Booking.room), selectinload(Booking.guest))
        .filter(Booking.estado == BookingStatus.PENDIENTE)
        .order_by(Booking.id.desc())
        .limit(1)
    )
    return result.scalars().first()

async def check_room_availability(db: AsyncSession, room_id: int, checkin: date, checkout: date) -> bool:
    """Verifica si la habitación no tiene reservas solapadas activas."""
    result = await db.execute(
        select(Booking).filter(
            Booking.room_id == room_id,
            Booking.estado.in_([BookingStatus.PENDIENTE, BookingStatus.CONFIRMADA]),
            Booking.fecha_checkin < checkout,
            Booking.fecha_checkout > checkin
        )
    )
    overlapping_booking = result.scalars().first()
    return overlapping_booking is None

async def create_booking(db: AsyncSession, booking_in: BookingCreate) -> Booking:
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

    # 1. Verificar disponibilidad
    is_available = await check_room_availability(
        db, booking_in.room_id, booking_in.fecha_checkin, booking_in.fecha_checkout
    )
    if not is_available:
        raise ValueError(f"La habitación ID {booking_in.room_id} ya no está disponible para las fechas seleccionadas.")

    # 2. Crear reserva en estado PENDIENTE
    booking = Booking(
        room_id=booking_in.room_id,
        guest_id=booking_in.guest_id,
        fecha_checkin=booking_in.fecha_checkin,
        fecha_checkout=booking_in.fecha_checkout,
        estado=BookingStatus.PENDIENTE,
        monto=booking_in.monto,
        referencia_pago=booking_in.referencia_pago
    )
    db.add(booking)
    await db.commit()
    await db.refresh(booking)

    # 3. Actualizar automáticamente la habitación a 'pendiente' (Amarillo) y notificar por WebSocket
    await update_room_status(db, booking_in.room_id, RoomStatus.PENDIENTE)

    # Cargar relaciones para respuesta completa
    return await get_booking_by_id(db, booking.id)

async def update_booking_status(
    db: AsyncSession, booking_id: int, new_status: BookingStatus, referencia_pago: Optional[str] = None
) -> Optional[Booking]:
    booking = await get_booking_by_id(db, booking_id)
    if not booking:
        return None

    booking.estado = new_status
    if referencia_pago:
        booking.referencia_pago = referencia_pago

    await db.commit()
    await db.refresh(booking)

    # Actualizar estado de la habitación correspondiente según el nuevo estado de la reserva
    if new_status == BookingStatus.CONFIRMADA:
        # Pago confirmado -> Habitación pasa a 'ocupada' (Rojo)
        await update_room_status(db, booking.room_id, RoomStatus.OCUPADA)
    elif new_status == BookingStatus.CANCELADA or new_status == BookingStatus.COMPLETADA:
        # Reserva cancelada o completada -> Habitación vuelve a 'disponible' (Verde)
        await update_room_status(db, booking.room_id, RoomStatus.DISPONIBLE)

    return booking
