from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


# ==========================================================
# Log Evidence
# ==========================================================


class IncidentLogEvidence(BaseModel):

    id: UUID

    timestamp: datetime

    level: str | None = None

    message: str | None = None

    source: str | None = None


# ==========================================================
# Metric Evidence
# ==========================================================


class IncidentMetricEvidence(BaseModel):

    timestamp: datetime

    cpu_usage: float | None = None

    memory_usage: float | None = None

    disk_usage: float | None = None

    disk_io_wait: float | None = None

    api_latency: float | None = None

    http_5xx_count: int | None = None

    http_4xx_count: int | None = None

    request_per_second: float | None = None


# ==========================================================
# Correlation Evidence
# ==========================================================


class IncidentCorrelationEvidence(BaseModel):

    correlation_group_id: UUID

    event_count: int | None = None

    primary_message: str | None = None

    first_seen: datetime | None = None

    last_seen: datetime | None = None


# ==========================================================
# Incident Information
# ==========================================================


class IncidentEvidenceIncident(BaseModel):

    incident_id: UUID

    title: str | None = None

    description: str | None = None

    incident_type: str | None = None

    severity: str | None = None

    status: str | None = None

    source: str | None = None

    created_at: datetime | None = None


# ==========================================================
# Metrics Summary
# ==========================================================


class IncidentMetricsSummary(BaseModel):

    cpu_usage_avg: float | None = None

    cpu_usage_max: float | None = None

    memory_usage_avg: float | None = None

    memory_usage_max: float | None = None

    disk_usage_avg: float | None = None

    disk_usage_max: float | None = None

    disk_io_wait_avg: float | None = None

    api_latency_avg: float | None = None

    api_latency_max: float | None = None

    total_http_4xx: int = 0

    total_http_5xx: int = 0

    request_per_second_avg: float | None = None


# ==========================================================
# Complete Incident Evidence Package
# ==========================================================


class IncidentEvidencePackage(BaseModel):

    incident: IncidentEvidenceIncident

    correlation: IncidentCorrelationEvidence | None = None

    logs: list[IncidentLogEvidence] = Field(
        default_factory=list
    )

    metrics: list[IncidentMetricEvidence] = Field(
        default_factory=list
    )

    metrics_summary: IncidentMetricsSummary

    evidence_window_start: datetime | None = None

    evidence_window_end: datetime | None = None