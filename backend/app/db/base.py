# Importa la Base y todos los modelos para que Alembic los detecte automáticamente
from app.db.base_class import Base
from app.models.room import Room
from app.models.guest import Guest
from app.models.booking import Booking
from app.models.payment import Payment
