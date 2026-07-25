import enum
from datetime import date
from typing import List, Optional, TYPE_CHECKING
from sqlalchemy import String, Numeric, Date, Enum, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base_class import Base

if TYPE_CHECKING:
    from app.models.room import Room
    from app.models.guest import Guest
    from app.models.payment import Payment

class BookingStatus(str, enum.Enum):
    PENDIENTE = "pendiente"    # Pre-reserva creada por el agente, esperando pago
    CONFIRMADA = "confirmada"  # Pago recibido exitosamente
    CANCELADA = "cancelada"
    COMPLETADA = "completada"  # Checkout finalizado

class Booking(Base):
    __tablename__ = "bookings"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    room_id: Mapped[int] = mapped_column(ForeignKey("rooms.id", ondelete="CASCADE"), nullable=False, index=True)
    guest_id: Mapped[int] = mapped_column(ForeignKey("guests.id", ondelete="CASCADE"), nullable=False, index=True)
    fecha_checkin: Mapped[date] = mapped_column(Date, nullable=False)
    fecha_checkout: Mapped[date] = mapped_column(Date, nullable=False)
    estado: Mapped[BookingStatus] = mapped_column(Enum(BookingStatus), default=BookingStatus.PENDIENTE, index=True, nullable=False)
    monto: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    referencia_pago: Mapped[Optional[str]] = mapped_column(String(100), unique=True, nullable=True, index=True)

    # Relaciones
    room: Mapped["Room"] = relationship("Room", back_populates="bookings")
    guest: Mapped["Guest"] = relationship("Guest", back_populates="bookings")
    payments: Mapped[List["Payment"]] = relationship("Payment", back_populates="booking", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Booking(id={self.id}, room_id={self.room_id}, guest_id={self.guest_id}, estado='{self.estado}')>"
