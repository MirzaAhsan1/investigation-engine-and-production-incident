import uuid

from sqlalchemy import (
    ForeignKey,
    Integer,
    String,
    DateTime,
)

from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from app.db.base import Base
from app.db.base_model import BaseModel


class CorrelationGroup(Base, BaseModel):

    __tablename__ = "correlation_groups"

    # ==========================================
    # Client
    # ==========================================

    client_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("clients.id"),
        nullable=False,
        index=True,
    )

    # ==========================================
    # Server
    # ==========================================

    server_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("servers.id"),
        nullable=False,
        index=True,
    )

    # ==========================================
    # Application
    # ==========================================

    application_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("applications.id"),
        nullable=False,
        index=True,
    )

    # ==========================================
    # Correlation Information
    # ==========================================

    correlation_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="UNKNOWN",
    )

    status: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        default="OPEN",
    )

    # ==========================================
    # Time Statistics
    # ==========================================

    first_seen: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    last_seen: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    event_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )

    # ==========================================
    # Incident
    # ==========================================

    incident_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey(
            "incidents.id",
            ondelete="SET NULL",
        ),
        nullable=True,
        index=True,
    )

    # ==========================================
    # Relationships
    # ==========================================

    logs = relationship(
        "LogEvent",
        back_populates="correlation_group",
    )

    incident = relationship(
        "Incident",
        back_populates="correlation_groups",
    )