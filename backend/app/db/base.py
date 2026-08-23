"""Importa ``Base`` y todos los modelos para que Alembic detecte el metadata."""

from app.db.base_class import Base
from app.models.booking import Booking
from app.models.guest import Guest
from app.models.payment import Payment
from app.models.room import Room

__all__ = ["Base", "Room", "Guest", "Booking", "Payment"]
