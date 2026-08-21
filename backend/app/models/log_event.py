import uuid

from sqlalchemy import (
    String,
    Text,
    DateTime,
    Integer,
    ForeignKey,
    Index,
)

from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from sqlalchemy.sql import func

from app.db.base import Base
from app.db.base_model import BaseModel


class LogEvent(Base, BaseModel):

    __tablename__ = "log_events"

    # ==========================================
    # Relationships / Ownership
    # ==========================================

    client_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("clients.id"),
        nullable=False,
        index=True,
    )

    server_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("servers.id"),
        nullable=False,
        index=True,
    )

    application_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("applications.id"),
        nullable=False,
        index=True,
    )

    # ==========================================
    # Log Information
    # ==========================================

    level: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        index=True,
    )

    message: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    timestamp: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        index=True,
    )

    # ==========================================
    # Deduplication
    # ==========================================

    fingerprint: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
        index=True,
    )

    occurrence_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=1,
        server_default="1",
    )

    first_seen: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    last_seen: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    # ==========================================
    # Processing Status
    # ==========================================

    status: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        default="PENDING",
        index=True,
    )
        # ==========================================
    # NEW: Correlation
    # ==========================================
    correlation_group_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey(
            "correlation_groups.id",
            ondelete="SET NULL",
        ),
        nullable=True,
        index=True,
    )
    
    correlation_group = relationship(
        "CorrelationGroup",
        back_populates="logs",
    )

    # ==========================================
    # Relationships
    # ==========================================

    client = relationship(
        "Client",
    )

    server = relationship(
        "Server",
    )

    application = relationship(
        "Application",
    )

    # ==========================================
    # Indexes
    # ==========================================

    __table_args__ = (
        Index(
            "ix_log_events_dedup_lookup",
            "client_id",
            "server_id",
            "application_id",
            "fingerprint",
            "last_seen",
        ),
    )
    