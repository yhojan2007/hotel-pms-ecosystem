from sqlalchemy.orm import DeclarativeBase, declared_attr
from datetime import datetime, timezone
from sqlalchemy import DateTime, func
from sqlalchemy.orm import Mapped, mapped_column

class Base(DeclarativeBase):
    id: Mapped[int]
    
    # Genera automáticamente el nombre de la tabla en minúsculas
    @declared_attr.directive
    def __tablename__(cls) -> str:
        return cls.__name__.lower() + "s"

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )
