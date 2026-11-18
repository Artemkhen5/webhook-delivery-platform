from datetime import datetime
from typing import Any
from uuid import UUID, uuid7

from sqlalchemy import DateTime, func, String
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID as PostgreSQLUUID, JSONB

from wdp.db.base import Base


class OutboxMessage(Base):
    __tablename__ = 'outbox_messages'

    id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        primary_key=True,
        default=uuid7
    )
    aggregate_type: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    aggregate_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        nullable=False,
    )
    message_type: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    payload: Mapped[dict[str, Any]] = mapped_column(
        JSONB,
        nullable=False,
    )
    published_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now()
    )
