import enum
from typing import List, TYPE_CHECKING
from sqlalchemy import String, Numeric, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base_class import Base

if TYPE_CHECKING:
    from app.models.booking import Booking

class RoomStatus(str, enum.Enum):
    DISPONIBLE = "disponible"  # Verde en el PMS
    PENDIENTE = "pendiente"    # Amarillo en el PMS (reserva creada, esperando pago)
    OCUPADA = "ocupada"        # Rojo en el PMS (pago confirmado / checkout pendiente)

class RoomType(str, enum.Enum):
    INDIVIDUAL = "individual"
    DOBLE = "doble"
    SUITE = "suite"
    DELUXE = "deluxe"

class Room(Base):
    __tablename__ = "rooms"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    nombre: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    tipo: Mapped[RoomType] = mapped_column(Enum(RoomType), default=RoomType.INDIVIDUAL, nullable=False)
    precio_base: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    estado: Mapped[RoomStatus] = mapped_column(Enum(RoomStatus), default=RoomStatus.DISPONIBLE, index=True, nullable=False)

    # Relación con Reservas
    bookings: Mapped[List["Booking"]] = relationship("Booking", back_populates="room", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Room(id={self.id}, nombre='{self.nombre}', tipo='{self.tipo}', estado='{self.estado}')>"
