from datetime import datetime
from typing import Any
from uuid import UUID, uuid7

from sqlalchemy import ForeignKey, DateTime, func, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID as PostgreSQLUUID, JSONB

from wdp.db.base import Base


class Event(Base):
    __tablename__ = 'events'

    id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        primary_key=True,
        default=uuid7
    )
    account_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey('accounts.id'),
        nullable=False
    )
    event_type: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )
    payload: Mapped[dict[str, Any]] = mapped_column(
        JSONB,
        nullable=False
    )
    idempotency_key: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now()
    )

    __table_args__ = (
        UniqueConstraint(
            "account_id",
            "idempotency_key",
            name="uq_events_account_id_idempotency_key"
        ),
    )
