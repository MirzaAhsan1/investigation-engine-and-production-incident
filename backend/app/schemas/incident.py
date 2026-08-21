from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.models.enums import (
    IncidentTypeEnum,
    SeverityEnum,
    StatusEnum,
    IncidentSourceEnum,
)


# ============================================================
# Create Incident
# ============================================================

class IncidentCreate(BaseModel):

    title: str

    description: str

    incident_type: IncidentTypeEnum

    severity: SeverityEnum

    source: IncidentSourceEnum


# ============================================================
# Application / Container
# ============================================================

class IncidentApplicationResponse(BaseModel):

    id: UUID

    server_id: UUID

    name: str

    container_name: str

    provider: str | None = None

    resource_uuid: str | None = None

    model_config = ConfigDict(
        from_attributes=True
    )


# ============================================================
# Investigation Summary
# ============================================================

class InvestigationSummaryResponse(BaseModel):

    id: UUID

    predicted_category: str | None = None

    predicted_cause: str | None = None

    root_cause: str | None = None

    confidence: float | None = None

    risk_score: float | None = None

    analysis_status: str | None = None

    model_config = ConfigDict(
        from_attributes=True
    )


# ============================================================
# Basic Incident Response
# ============================================================

class IncidentResponse(BaseModel):

    id: UUID

    title: str

    description: str

    incident_type: IncidentTypeEnum

    severity: SeverityEnum

    status: StatusEnum

    source: IncidentSourceEnum

    reported_by: UUID

    assigned_to: UUID | None = None

    # Application / Container
    application_id: UUID | None = None

    application: IncidentApplicationResponse | None = None

    investigation: InvestigationSummaryResponse | None = None

    created_at: datetime

    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )


# ============================================================
# Incident List
# ============================================================

class IncidentListResponse(BaseModel):

    items: list[IncidentResponse]

    total: int


# ============================================================
# Incident Update
# ============================================================

class IncidentUpdate(BaseModel):

    title: str | None = None

    description: str | None = None

    severity: SeverityEnum | None = None

    status: StatusEnum | None = None

    assigned_to: UUID | None = None


# ============================================================
# Correlation Group
# ============================================================

class CorrelationGroupIncidentResponse(BaseModel):

    id: UUID

    application_id: UUID

    client_id: UUID

    server_id: UUID

    event_count: int

    first_seen: datetime | None = None

    last_seen: datetime | None = None

    incident_id: UUID | None = None

    model_config = ConfigDict(
        from_attributes=True
    )


# ============================================================
# Evidence
# ============================================================

class EvidenceIncidentResponse(BaseModel):

    id: UUID

    incident_id: UUID | None = None

    # --------------------------------------------------------
    # Log Evidence
    # --------------------------------------------------------

    log_count: int

    error_count: int

    warning_count: int

    first_seen: datetime | None = None

    last_seen: datetime | None = None

    error_rate: float | None = None

    database_timeout_count: int | None = None

    logs: str

    # --------------------------------------------------------
    # Infrastructure Metrics
    # --------------------------------------------------------

    cpu_usage: float | None = None

    memory_usage: float | None = None

    disk_usage: float | None = None

    disk_io_wait: float | None = None

    # --------------------------------------------------------
    # Network / API Metrics
    # --------------------------------------------------------

    api_latency: int | None = None

    network_latency: int | None = None

    packet_loss: float | None = None

    request_per_second: int | None = None

    # --------------------------------------------------------
    # Application Metrics
    # --------------------------------------------------------

    http_5xx_count: int | None = None

    http_4xx_count: int | None = None

    restart_count: int | None = None

    active_containers: int | None = None

    pod_restart_count: int | None = None

    deployment_changed: bool | None = None

    # --------------------------------------------------------
    # Database Metrics
    # --------------------------------------------------------

    db_connections: int | None = None

    # --------------------------------------------------------
    # Security Metrics
    # --------------------------------------------------------

    failed_login_attempts: int | None = None

    ssl_certificate_days_left: int | None = None

    # --------------------------------------------------------
    # Service Information
    # --------------------------------------------------------

    service_name: str | None = None

    environment: str | None = None

    model_config = ConfigDict(
        from_attributes=True
    )


# ============================================================
# Complete Incident Detail
# ============================================================

class IncidentDetailResponse(BaseModel):

    # --------------------------------------------------------
    # Main Incident
    # --------------------------------------------------------

    incident: IncidentResponse

    # --------------------------------------------------------
    # Application / Container
    # --------------------------------------------------------

    application: (
        IncidentApplicationResponse
        | None
    ) = None

    # --------------------------------------------------------
    # Correlation Group
    # --------------------------------------------------------

    correlation_group: (
        CorrelationGroupIncidentResponse
        | None
    ) = None

    # --------------------------------------------------------
    # Evidence
    # --------------------------------------------------------

    evidence: (
        EvidenceIncidentResponse
        | None
    ) = None