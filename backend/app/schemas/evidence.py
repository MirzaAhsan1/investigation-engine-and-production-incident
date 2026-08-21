from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class EvidenceCreate(BaseModel):

    incident_id: UUID

    # ==========================================================
    # Log Summary
    # ==========================================================

    log_count: int = 0
    error_count: int = 0
    warning_count: int = 0

    first_seen: datetime | None = None
    last_seen: datetime | None = None

    # ==========================================================
    # Infrastructure Metrics
    # ==========================================================

    cpu_usage: float | None = None
    memory_usage: float | None = None
    disk_usage: float | None = None
    disk_io_wait: float | None = None

    # ==========================================================
    # Network / API Metrics
    # ==========================================================

    api_latency: int | None = None
    network_latency: int | None = None
    packet_loss: float | None = None
    request_per_second: int | None = None

    # ==========================================================
    # Application Metrics
    # ==========================================================

    error_rate: float | None = None
    http_5xx_count: int | None = None
    http_4xx_count: int | None = None

    restart_count: int | None = None
    active_containers: int | None = None
    pod_restart_count: int | None = None

    deployment_changed: bool | None = None

    # ==========================================================
    # Database Metrics
    # ==========================================================

    db_connections: int | None = None
    database_timeout_count: int | None = None

    # ==========================================================
    # Security Metrics
    # ==========================================================

    failed_login_attempts: int | None = None
    ssl_certificate_days_left: int | None = None

    # ==========================================================
    # Service Information
    # ==========================================================

    service_name: str | None = None
    environment: str | None = None

    # ==========================================================
    # Aggregated Logs
    # ==========================================================

    logs: Any = ""


class EvidenceResponse(BaseModel):

    model_config = ConfigDict(
        from_attributes=True,
    )

    id: UUID
    incident_id: UUID

    # ==========================================================
    # Log Summary
    # ==========================================================

    log_count: int
    error_count: int
    warning_count: int

    first_seen: datetime | None
    last_seen: datetime | None

    # ==========================================================
    # Infrastructure Metrics
    # ==========================================================

    cpu_usage: float | None
    memory_usage: float | None
    disk_usage: float | None
    disk_io_wait: float | None

    # ==========================================================
    # Network / API Metrics
    # ==========================================================

    api_latency: int | None
    network_latency: int | None
    packet_loss: float | None
    request_per_second: int | None

    # ==========================================================
    # Application Metrics
    # ==========================================================

    error_rate: float | None
    http_5xx_count: int | None
    http_4xx_count: int | None

    restart_count: int | None
    active_containers: int | None
    pod_restart_count: int | None

    deployment_changed: bool | None

    # ==========================================================
    # Database Metrics
    # ==========================================================

    db_connections: int | None
    database_timeout_count: int | None

    # ==========================================================
    # Security Metrics
    # ==========================================================

    failed_login_attempts: int | None
    ssl_certificate_days_left: int | None

    # ==========================================================
    # Service Information
    # ==========================================================

    service_name: str | None
    environment: str | None

    # ==========================================================
    # Aggregated Logs
    # ==========================================================

    logs: Any

    created_at: datetime
    updated_at: datetime