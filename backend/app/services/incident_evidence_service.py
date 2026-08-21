from datetime import datetime, timedelta
from uuid import UUID

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.incident import Incident
from app.models.correlation_group import CorrelationGroup
from app.models.system_metric import SystemMetric

from app.schemas.incident_evidence import (
    IncidentCorrelationEvidence,
    IncidentEvidenceIncident,
    IncidentEvidencePackage,
    IncidentLogEvidence,
    IncidentMetricEvidence,
    IncidentMetricsSummary,
)


# ==========================================================
# Evidence Window
# ==========================================================

EVIDENCE_WINDOW_MINUTES = 15


# ==========================================================
# Get Incident
# ==========================================================

def get_incident(
    db: Session,
    incident_id: UUID,
):
    return (
        db.query(Incident)
        .filter(
            Incident.id == incident_id
        )
        .first()
    )


# ==========================================================
# Get Correlation Group
# ==========================================================

def get_correlation_group(
    db: Session,
    incident: Incident,
):
    if incident.correlation_group_id is None:
        return None

    return (
        db.query(CorrelationGroup)
        .filter(
            CorrelationGroup.id
            == incident.correlation_group_id
        )
        .first()
    )


# ==========================================================
# Get Evidence Time Window
# ==========================================================

def get_evidence_window(
    incident: Incident,
    correlation_group: CorrelationGroup | None,
):
    if correlation_group is not None:

        first_seen = getattr(
            correlation_group,
            "first_seen",
            None,
        )

        last_seen = getattr(
            correlation_group,
            "last_seen",
            None,
        )

        if first_seen and last_seen:
            return first_seen, last_seen

    incident_time = getattr(
        incident,
        "created_at",
        None,
    )

    if incident_time is None:
        return None, None

    return (
        incident_time
        - timedelta(
            minutes=EVIDENCE_WINDOW_MINUTES
        ),
        incident_time
        + timedelta(
            minutes=EVIDENCE_WINDOW_MINUTES
        ),
    )


# ==========================================================
# Get System Metrics
# ==========================================================

def get_system_metrics(
    db: Session,
    incident: Incident,
    start_time: datetime | None,
    end_time: datetime | None,
):
    query = (
        db.query(SystemMetric)
        .filter(
            SystemMetric.client_id
            == incident.reported_by
        )
    )

    if start_time is not None:

        query = query.filter(
            SystemMetric.timestamp
            >= start_time
        )

    if end_time is not None:

        query = query.filter(
            SystemMetric.timestamp
            <= end_time
        )

    return (
        query
        .order_by(
            SystemMetric.timestamp.asc()
        )
        .all()
    )


# ==========================================================
# Convert Metrics
# ==========================================================

def build_metric_evidence(
    metrics,
):
    evidence = []

    for metric in metrics:

        evidence.append(
            IncidentMetricEvidence(
                timestamp=metric.timestamp,

                cpu_usage=metric.cpu_usage,

                memory_usage=metric.memory_usage,

                disk_usage=metric.disk_usage,

                disk_io_wait=metric.disk_io_wait,

                api_latency=metric.api_latency,

                http_5xx_count=(
                    metric.http_5xx_count
                ),

                http_4xx_count=(
                    metric.http_4xx_count
                ),

                request_per_second=(
                    metric.request_per_second
                ),
            )
        )

    return evidence


# ==========================================================
# Build Metrics Summary
# ==========================================================

def build_metrics_summary(
    metrics,
):
    if not metrics:

        return IncidentMetricsSummary(
            total_http_4xx=0,
            total_http_5xx=0,
        )

    cpu_values = [
        metric.cpu_usage
        for metric in metrics
        if metric.cpu_usage is not None
    ]

    memory_values = [
        metric.memory_usage
        for metric in metrics
        if metric.memory_usage is not None
    ]

    disk_values = [
        metric.disk_usage
        for metric in metrics
        if metric.disk_usage is not None
    ]

    disk_io_wait_values = [
        metric.disk_io_wait
        for metric in metrics
        if metric.disk_io_wait is not None
    ]

    latency_values = [
        metric.api_latency
        for metric in metrics
        if metric.api_latency is not None
    ]

    rps_values = [
        metric.request_per_second
        for metric in metrics
        if metric.request_per_second is not None
    ]

    total_http_4xx = sum(
        metric.http_4xx_count or 0
        for metric in metrics
    )

    total_http_5xx = sum(
        metric.http_5xx_count or 0
        for metric in metrics
    )

    return IncidentMetricsSummary(

        cpu_usage_avg=(
            sum(cpu_values) / len(cpu_values)
            if cpu_values
            else None
        ),

        cpu_usage_max=(
            max(cpu_values)
            if cpu_values
            else None
        ),

        memory_usage_avg=(
            sum(memory_values)
            / len(memory_values)
            if memory_values
            else None
        ),

        memory_usage_max=(
            max(memory_values)
            if memory_values
            else None
        ),

        disk_usage_avg=(
            sum(disk_values)
            / len(disk_values)
            if disk_values
            else None
        ),

        disk_usage_max=(
            max(disk_values)
            if disk_values
            else None
        ),

        disk_io_wait_avg=(
            sum(disk_io_wait_values)
            / len(disk_io_wait_values)
            if disk_io_wait_values
            else None
        ),

        api_latency_avg=(
            sum(latency_values)
            / len(latency_values)
            if latency_values
            else None
        ),

        api_latency_max=(
            max(latency_values)
            if latency_values
            else None
        ),

        total_http_4xx=total_http_4xx,

        total_http_5xx=total_http_5xx,

        request_per_second_avg=(
            sum(rps_values)
            / len(rps_values)
            if rps_values
            else None
        ),
    )


# ==========================================================
# Build Correlation Evidence
# ==========================================================

def build_correlation_evidence(
    correlation_group,
):
    if correlation_group is None:
        return None

    return IncidentCorrelationEvidence(

        correlation_group_id=(
            correlation_group.id
        ),

        event_count=getattr(
            correlation_group,
            "event_count",
            None,
        ),

        primary_message=getattr(
            correlation_group,
            "primary_message",
            None,
        ),

        first_seen=getattr(
            correlation_group,
            "first_seen",
            None,
        ),

        last_seen=getattr(
            correlation_group,
            "last_seen",
            None,
        ),
    )


# ==========================================================
# Build Incident Evidence
# ==========================================================

def build_incident_evidence(
    incident: Incident,
):
    return IncidentEvidenceIncident(

        incident_id=incident.id,

        title=incident.title,

        description=incident.description,

        incident_type=incident.incident_type,

        severity=incident.severity,

        status=incident.status,

        source=incident.source,

        created_at=getattr(
            incident,
            "created_at",
            None,
        ),
    )


# ==========================================================
# Main Evidence Aggregator
# ==========================================================

def build_incident_evidence_package(
    db: Session,
    incident_id: UUID,
):
    # ======================================================
    # 1. Get Incident
    # ======================================================

    incident = get_incident(
        db=db,
        incident_id=incident_id,
    )

    if incident is None:
        return None

    # ======================================================
    # 2. Get Correlation Group
    # ======================================================

    correlation_group = (
        get_correlation_group(
            db=db,
            incident=incident,
        )
    )

    # ======================================================
    # 3. Determine Evidence Window
    # ======================================================

    (
        start_time,
        end_time,
    ) = get_evidence_window(
        incident=incident,
        correlation_group=correlation_group,
    )

    # ======================================================
    # 4. Get System Metrics
    # ======================================================

    metrics = get_system_metrics(
        db=db,
        incident=incident,
        start_time=start_time,
        end_time=end_time,
    )

    # ======================================================
    # 5. Build Metric Evidence
    # ======================================================

    metric_evidence = (
        build_metric_evidence(
            metrics=metrics,
        )
    )

    # ======================================================
    # 6. Build Metric Summary
    # ======================================================

    metrics_summary = (
        build_metrics_summary(
            metrics=metrics,
        )
    )

    # ======================================================
    # 7. Build Correlation Evidence
    # ======================================================

    correlation_evidence = (
        build_correlation_evidence(
            correlation_group=correlation_group,
        )
    )

    # ======================================================
    # 8. Build Incident Evidence
    # ======================================================

    incident_evidence = (
        build_incident_evidence(
            incident=incident,
        )
    )

    # ======================================================
    # 9. Build Final Package
    # ======================================================

    return IncidentEvidencePackage(

        incident=incident_evidence,

        correlation=correlation_evidence,

        logs=[],

        metrics=metric_evidence,

        metrics_summary=metrics_summary,

        evidence_window_start=start_time,

        evidence_window_end=end_time,
    )