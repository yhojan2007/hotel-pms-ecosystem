"""Modelo ORM de pago asociado a una reserva."""

import enum
from typing import TYPE_CHECKING, Optional

from sqlalchemy import Enum, ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base

if TYPE_CHECKING:
    from app.models.booking import Booking


class PaymentStatus(str, enum.Enum):
    """Resultado del intento de cobro."""

    PENDIENTE = "pendiente"
    CONFIRMADO = "confirmado"
    FALLIDO = "fallido"


class Payment(Base):
    """Cobro registrado por un proveedor (mock, Wallbit, MercadoPago, Stripe)."""

    __tablename__ = "payments"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    booking_id: Mapped[int] = mapped_column(
        ForeignKey("bookings.id", ondelete="CASCADE"), nullable=False, index=True
    )
    estado: Mapped[PaymentStatus] = mapped_column(
        Enum(PaymentStatus), default=PaymentStatus.PENDIENTE, index=True, nullable=False
    )
    monto: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    proveedor: Mapped[str] = mapped_column(String(50), default="mock_gateway", nullable=False)
    referencia_externa: Mapped[Optional[str]] = mapped_column(String(100), unique=True, nullable=True, index=True)

    booking: Mapped["Booking"] = relationship("Booking", back_populates="payments")

    def __repr__(self) -> str:
        return (
            f"<Payment(id={self.id}, booking_id={self.booking_id}, "
            f"estado='{self.estado}', monto={self.monto})>"
        )
