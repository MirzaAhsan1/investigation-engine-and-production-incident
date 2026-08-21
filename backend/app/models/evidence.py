import uuid

from sqlalchemy import (
    Float,
    ForeignKey,
    Integer,
    String,
    Boolean,
    Text,
    DateTime,
)

from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from app.db.base import Base
from app.db.base_model import BaseModel


class Evidence(Base, BaseModel):

    __tablename__ = "evidence"

    # ==========================================================
    # Incident
    # ==========================================================

    incident_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("incidents.id"),
        nullable=True,
        # unique=True,
        index=True,
    )

    # ==========================================================
    # Correlation / Log Summary
    # ==========================================================

    log_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )

    error_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )

    warning_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )

    first_seen: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    last_seen: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
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
    # Network / API Metrics
    # ==========================================================

    api_latency: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    network_latency: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    packet_loss: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    request_per_second: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    # ==========================================================
    # Application Metrics
    # ==========================================================

    error_rate: Mapped[float | None] = mapped_column(
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

    restart_count: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    active_containers: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    pod_restart_count: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    deployment_changed: Mapped[bool | None] = mapped_column(
        Boolean,
        nullable=True,
    )

    # ==========================================================
    # Database Metrics
    # ==========================================================

    db_connections: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    database_timeout_count: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    # ==========================================================
    # Security Metrics
    # ==========================================================

    failed_login_attempts: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    ssl_certificate_days_left: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    # ==========================================================
    # Service Information
    # ==========================================================

    service_name: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    environment: Mapped[str | None] = mapped_column(
        String(30),
        nullable=True,
    )

    # ==========================================================
    # Aggregated Logs
    # ==========================================================

    logs: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    # ==========================================================
    # Relationship
    # ==========================================================

    incident = relationship(
        "Incident",
        back_populates="evidence",
    )
    # ==========================================================
# Correlation Group
# ==========================================================

    correlation_group_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("correlation_groups.id"),
        nullable=True,
        unique=True,
        index=True,
    )