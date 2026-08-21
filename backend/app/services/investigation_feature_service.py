from datetime import datetime, timedelta
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.incident import Incident
from app.models.system_metric import SystemMetric


# ==========================================================
# Configuration
# ==========================================================

EVIDENCE_WINDOW_MINUTES = 10


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
# Get Evidence Time Window
# ==========================================================

def get_evidence_window(
    incident: Incident,
):
    end_time = datetime.now(
        incident.created_at.tzinfo
    )

    start_time = (
        end_time
        - timedelta(
            minutes=EVIDENCE_WINDOW_MINUTES
        )
    )

    return start_time, end_time


# ==========================================================
# Get System Metrics
# ==========================================================

def get_system_metrics(
    db: Session,
    incident: Incident,
    start_time: datetime,
    end_time: datetime,
):
    return (
        db.query(SystemMetric)
        .filter(
            SystemMetric.client_id
            == incident.reported_by,

            SystemMetric.timestamp
            >= start_time,

            SystemMetric.timestamp
            <= end_time,
        )
        .order_by(
            SystemMetric.timestamp.asc()
        )
        .all()
    )


# ==========================================================
# Calculate Average
# ==========================================================

def calculate_average(
    values: list[float],
):
    if not values:
        return None

    return sum(values) / len(values)


# ==========================================================
# Calculate Maximum
# ==========================================================

def calculate_maximum(
    values: list[float],
):
    if not values:
        return None

    return max(values)


# ==========================================================
# Build Investigation Features
# ==========================================================

def build_investigation_features(
    db: Session,
    incident_id: UUID,
):
    # ------------------------------------------------------
    # 1. Get Incident
    # ------------------------------------------------------

    incident = get_incident(
        db=db,
        incident_id=incident_id,
    )

    if incident is None:
        return None


    # ------------------------------------------------------
    # 2. Evidence Window
    # ------------------------------------------------------

    start_time, end_time = (
        get_evidence_window(
            incident=incident,
        )
    )


    # ------------------------------------------------------
    # 3. Get Metrics
    # ------------------------------------------------------

    metrics = get_system_metrics(
        db=db,
        incident=incident,
        start_time=start_time,
        end_time=end_time,
    )


    # ------------------------------------------------------
    # 4. Extract Metric Values
    # ------------------------------------------------------

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

    api_latency_values = [
        metric.api_latency
        for metric in metrics
        if metric.api_latency is not None
    ]

    http_4xx_values = [
        metric.http_4xx_count
        for metric in metrics
        if metric.http_4xx_count is not None
    ]

    http_5xx_values = [
        metric.http_5xx_count
        for metric in metrics
        if metric.http_5xx_count is not None
    ]

    request_per_second_values = [
        metric.request_per_second
        for metric in metrics
        if metric.request_per_second is not None
    ]


    # ------------------------------------------------------
    # 5. Build Model Features
    # ------------------------------------------------------

    features = {

        "incident_id": str(
            incident.id
        ),

        "evidence_start": start_time,

        "evidence_end": end_time,

        # ------------------------------
        # Infrastructure
        # ------------------------------

        "cpu_usage_avg": calculate_average(
            cpu_values
        ),

        "cpu_usage_max": calculate_maximum(
            cpu_values
        ),

        "memory_usage_avg": calculate_average(
            memory_values
        ),

        "memory_usage_max": calculate_maximum(
            memory_values
        ),

        "disk_usage_avg": calculate_average(
            disk_values
        ),

        "disk_usage_max": calculate_maximum(
            disk_values
        ),

        "disk_io_wait_avg": calculate_average(
            disk_io_wait_values
        ),

        "disk_io_wait_max": calculate_maximum(
            disk_io_wait_values
        ),

        # ------------------------------
        # HTTP
        # ------------------------------

        "api_latency_avg": calculate_average(
            api_latency_values
        ),

        "api_latency_max": calculate_maximum(
            api_latency_values
        ),

        "http_4xx_total": sum(
            http_4xx_values
        ),

        "http_5xx_total": sum(
            http_5xx_values
        ),

        "request_per_second_avg": calculate_average(
            request_per_second_values
        ),

        "request_per_second_max": calculate_maximum(
            request_per_second_values
        ),

        # ------------------------------
        # Evidence
        # ------------------------------

        "metric_samples": len(
            metrics
        ),
    }


    return features