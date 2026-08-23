"""Casos de uso de habitaciones (CRUD + notificación en tiempo real)."""

from typing import Any, Dict, List, Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.api.ws import notify_room_status_change
from app.models.room import Room, RoomStatus
from app.schemas.room import RoomCreate


async def get_all_rooms(db: AsyncSession) -> List[Room]:
    """Devuelve todas las habitaciones ordenadas por ID."""
    result = await db.execute(select(Room).order_by(Room.id))
    return list(result.scalars().all())


async def get_room_by_id(db: AsyncSession, room_id: int) -> Optional[Room]:
    """Busca una habitación por clave primaria."""
    result = await db.execute(select(Room).filter(Room.id == room_id))
    return result.scalars().first()


async def create_room(db: AsyncSession, room_in: RoomCreate) -> Room:
    """Persiste una habitación nueva."""
    room = Room(
        nombre=room_in.nombre,
        tipo=room_in.tipo,
        precio_base=room_in.precio_base,
        estado=room_in.estado,
    )
    db.add(room)
    await db.commit()
    await db.refresh(room)
    return room


async def update_room_status(db: AsyncSession, room_id: int, new_status: RoomStatus) -> Optional[Room]:
    """Actualiza el estado y emite ``room_status_updated`` por WebSocket."""
    room = await get_room_by_id(db, room_id)
    if not room:
        return None

    room.estado = new_status
    await db.commit()
    await db.refresh(room)

    room_payload: Dict[str, Any] = {
        "id": room.id,
        "nombre": room.nombre,
        "tipo": room.tipo.value,
        "precio_base": float(room.precio_base),
        "estado": room.estado.value,
        "updated_at": room.updated_at.isoformat(),
    }
    await notify_room_status_change(room_payload)

    return room
