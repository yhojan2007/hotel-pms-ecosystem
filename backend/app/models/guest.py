"""Modelo ORM de huésped."""

from typing import TYPE_CHECKING, List

from sqlalchemy import Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base

if TYPE_CHECKING:
    from app.models.booking import Booking


class Guest(Base):
    """Huésped identificado por contacto (WhatsApp / teléfono) único."""

    __tablename__ = "guests"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    nombre: Mapped[str] = mapped_column(String(100), nullable=False)
    contacto: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    historial_gasto: Mapped[float] = mapped_column(Numeric(10, 2), default=0.00, nullable=False)

    bookings: Mapped[List["Booking"]] = relationship(
        "Booking", back_populates="guest", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Guest(id={self.id}, nombre='{self.nombre}', contacto='{self.contacto}')>"
