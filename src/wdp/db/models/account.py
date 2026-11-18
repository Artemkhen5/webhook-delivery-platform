from datetime import datetime
from uuid import UUID, uuid7

from sqlalchemy import String, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID as PostgreSQLUUID

from wdp.db.base import Base


class Account(Base):
    __tablename__ = 'accounts'

    id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        primary_key=True,
        default=uuid7
    )
    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    api_key_hash: Mapped[str] = mapped_column(
        String(),
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
