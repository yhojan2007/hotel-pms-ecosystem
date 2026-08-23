"""Casos de uso de huéspedes."""

from typing import List, Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.models.guest import Guest
from app.schemas.guest import GuestCreate


async def get_all_guests(db: AsyncSession) -> List[Guest]:
    """Lista huéspedes, más recientes primero."""
    result = await db.execute(select(Guest).order_by(Guest.id.desc()))
    return list(result.scalars().all())


async def get_guest_by_id(db: AsyncSession, guest_id: int) -> Optional[Guest]:
    """Busca un huésped por ID."""
    result = await db.execute(select(Guest).filter(Guest.id == guest_id))
    return result.scalars().first()


async def get_guest_by_contacto(db: AsyncSession, contacto: str) -> Optional[Guest]:
    """Busca un huésped por número de WhatsApp / teléfono."""
    result = await db.execute(select(Guest).filter(Guest.contacto == contacto))
    return result.scalars().first()


async def create_guest(db: AsyncSession, guest_in: GuestCreate) -> Guest:
    """Crea el huésped o reutiliza el registro existente con el mismo contacto."""
    existing = await get_guest_by_contacto(db, guest_in.contacto)
    if existing:
        return existing

    guest = Guest(
        nombre=guest_in.nombre,
        contacto=guest_in.contacto,
        historial_gasto=guest_in.historial_gasto or 0.00,
    )
    db.add(guest)
    await db.commit()
    await db.refresh(guest)
    return guest


async def update_guest_spending(db: AsyncSession, guest_id: int, added_amount: float) -> Optional[Guest]:
    """Suma ``added_amount`` al historial de gasto del huésped."""
    guest = await get_guest_by_id(db, guest_id)
    if not guest:
        return None

    guest.historial_gasto = float(guest.historial_gasto) + float(added_amount)
    await db.commit()
    await db.refresh(guest)
    return guest
