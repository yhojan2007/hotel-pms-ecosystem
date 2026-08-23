"""Carga inicial de habitaciones de demo (idempotente)."""

from __future__ import annotations

import asyncio
import logging
from typing import Any

from sqlalchemy.future import select

from app.db.session import AsyncSessionLocal
from app.models.room import Room, RoomStatus, RoomType

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("seed")

SEED_ROOMS: list[dict[str, Any]] = [
    {"nombre": "Habitación 101", "tipo": RoomType.INDIVIDUAL, "precio_base": 45.00, "estado": RoomStatus.DISPONIBLE},
    {"nombre": "Habitación 102", "tipo": RoomType.INDIVIDUAL, "precio_base": 45.00, "estado": RoomStatus.DISPONIBLE},
    {"nombre": "Habitación 103", "tipo": RoomType.DOBLE, "precio_base": 75.00, "estado": RoomStatus.DISPONIBLE},
    {"nombre": "Habitación 104", "tipo": RoomType.DOBLE, "precio_base": 75.00, "estado": RoomStatus.DISPONIBLE},
    {"nombre": "Habitación 201", "tipo": RoomType.SUITE, "precio_base": 120.00, "estado": RoomStatus.DISPONIBLE},
    {"nombre": "Habitación 202", "tipo": RoomType.SUITE, "precio_base": 120.00, "estado": RoomStatus.DISPONIBLE},
    {"nombre": "Habitación 301", "tipo": RoomType.DELUXE, "precio_base": 200.00, "estado": RoomStatus.DISPONIBLE},
    {"nombre": "Habitación 302", "tipo": RoomType.DELUXE, "precio_base": 200.00, "estado": RoomStatus.DISPONIBLE},
]


async def seed_database() -> None:
    """Inserta 8 habitaciones si la tabla ``rooms`` está vacía."""
    async with AsyncSessionLocal() as session:
        logger.info("Verificando si la base de datos ya contiene habitaciones...")
        result = await session.execute(select(Room))
        existing_rooms = result.scalars().all()

        if existing_rooms:
            logger.info(f"La base de datos ya tiene {len(existing_rooms)} habitaciones. Omitiendo seed.")
            return

        logger.info("Insertando 8 habitaciones iniciales de prueba...")
        for r_data in SEED_ROOMS:
            room = Room(**r_data)
            session.add(room)

        await session.commit()
        logger.info("¡Seed ejecutado exitosamente! 8 habitaciones creadas.")


if __name__ == "__main__":
    asyncio.run(seed_database())
