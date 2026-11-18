from uuid import UUID, uuid7

from sqlalchemy import ForeignKey, Text, Index, UniqueConstraint, String
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID as PostgreSQLUUID

from wdp.db.base import Base


class EndpointSubscription(Base):
    __tablename__ = 'endpoint_subscriptions'

    id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        primary_key=True,
        default=uuid7
    )
    endpoint_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey('endpoints.id'),
        nullable=False
    )
    event_type: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )
    __table_args__ = (
        UniqueConstraint(
            "endpoint_id",
            "event_type",
            name="uq_endpoint_subscriptions_endpoint_event_type"
        ),
        Index("ix_endpoint_subscriptions_event_type", "event_type"),
    )
