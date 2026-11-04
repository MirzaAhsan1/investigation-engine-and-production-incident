import uuid

from sqlalchemy import (
    DateTime,
    Float,
    ForeignKey,
    Integer,
    Boolean
)

from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from app.db.base import Base
from app.db.base_model import BaseModel


class SystemMetric(Base, BaseModel):

    __tablename__ = "system_metrics"

    # ==========================================================
    # Ownership
    # ==========================================================

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

    # Server-wide metrics don't necessarily belong
    # to one application.
    application_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("applications.id"),
        nullable=True,
        index=True,
    )

    # ==========================================================
    # Timestamp
    # ==========================================================

    timestamp: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        index=True,
    )

    # ==========================================================
    # Infrastructure Metrics
    # ==========================================================

    cpu_usage: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    memory_usage: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    disk_usage: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    disk_io_wait: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    # ==========================================================
    # HTTP / Application Metrics
    # ==========================================================

    api_latency: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    http_5xx_count: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    http_4xx_count: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    request_per_second: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    request_count: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )
    
    active_containers: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )
    
    deployment_changed: Mapped[bool | None] = mapped_column(
        Boolean,
        nullable=True,
    )

    # ==========================================================
    # Relationships
    # ==========================================================

    client = relationship(
        "Client",
    )

    server = relationship(
        "Server",
    )

    application = relationship(
        "Application",
    )