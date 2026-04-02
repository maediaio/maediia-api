"""SQLAlchemy base models."""
from datetime import datetime
from sqlalchemy import DateTime, MetaData, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

# Shared metadata so ForeignKeys work across both base classes
_metadata = MetaData()


class Base(DeclarativeBase):
    """Base for mutable tables — has created_at + updated_at."""
    metadata = _metadata

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


class ReadOnlyBase(DeclarativeBase):
    """Base for append-only log tables — created_at only, no updated_at."""
    metadata = _metadata

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
