"""Declarative base de SQLAlchemy con timestamps comunes."""

from datetime import datetime

from sqlalchemy import DateTime, func
from sqlalchemy.orm import DeclarativeBase, Mapped, declared_attr, mapped_column


class Base(DeclarativeBase):
    """Base ORM: nombre de tabla por defecto y columnas ``created_at`` / ``updated_at``."""

    id: Mapped[int]

    @declared_attr.directive
    def __tablename__(cls) -> str:
        """Nombre de tabla: nombre de clase en minúsculas + ``s`` (p. ej. Room → rooms)."""
        return cls.__name__.lower() + "s"

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
