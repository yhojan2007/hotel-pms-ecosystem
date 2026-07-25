from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List, Optional
from app.models.room import Room, RoomStatus
from app.schemas.room import RoomCreate, RoomUpdate
from app.api.ws import notify_room_status_change

async def get_all_rooms(db: AsyncSession) -> List[Room]:
    result = await db.execute(select(Room).order_by(Room.id))
    return list(result.scalars().all())

async def get_room_by_id(db: AsyncSession, room_id: int) -> Optional[Room]:
    result = await db.execute(select(Room).filter(Room.id == room_id))
    return result.scalars().first()

async def create_room(db: AsyncSession, room_in: RoomCreate) -> Room:
    room = Room(
        nombre=room_in.nombre,
        tipo=room_in.tipo,
        precio_base=room_in.precio_base,
        estado=room_in.estado
    )
    db.add(room)
    await db.commit()
    await db.refresh(room)
    return room

async def update_room_status(db: AsyncSession, room_id: int, new_status: RoomStatus) -> Optional[Room]:
    room = await get_room_by_id(db, room_id)
    if not room:
        return None

    room.estado = new_status
    await db.commit()
    await db.refresh(room)

    # Notificar inmediatamente a todos los clientes suscritos al WebSocket
    room_payload = {
        "id": room.id,
        "nombre": room.nombre,
        "tipo": room.tipo.value,
        "precio_base": float(room.precio_base),
        "estado": room.estado.value,
        "updated_at": room.updated_at.isoformat()
    }
    await notify_room_status_change(room_payload)

    return room
