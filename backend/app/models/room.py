"""Modelo ORM de habitación y enums de tipo/estado (colores del PMS)."""

import enum
from typing import TYPE_CHECKING, List

from sqlalchemy import Enum, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base

if TYPE_CHECKING:
    from app.models.booking import Booking


class RoomStatus(str, enum.Enum):
    """Estado operativo de la habitación en el dashboard."""

    DISPONIBLE = "disponible"  # Verde
    PENDIENTE = "pendiente"  # Amarillo: reserva creada, esperando pago
    OCUPADA = "ocupada"  # Rojo: pago confirmado / checkout pendiente


class RoomType(str, enum.Enum):
    """Categoría comercial de la habitación."""

    INDIVIDUAL = "individual"
    DOBLE = "doble"
    SUITE = "suite"
    DELUXE = "deluxe"


class Room(Base):
    """Habitación inventariada: nombre único, tipo, tarifa base y estado."""

    __tablename__ = "rooms"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    nombre: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    tipo: Mapped[RoomType] = mapped_column(Enum(RoomType), default=RoomType.INDIVIDUAL, nullable=False)
    precio_base: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    estado: Mapped[RoomStatus] = mapped_column(
        Enum(RoomStatus), default=RoomStatus.DISPONIBLE, index=True, nullable=False
    )

    bookings: Mapped[List["Booking"]] = relationship(
        "Booking", back_populates="room", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Room(id={self.id}, nombre='{self.nombre}', tipo='{self.tipo}', estado='{self.estado}')>"
