from uuid import UUID

from datetime import timedelta

from sqlalchemy.orm import Session

from app.models.application import Application
from app.models.correlation_group import CorrelationGroup
from app.models.evidence import Evidence
from app.models.incident import Incident
from app.models.log_event import LogEvent
from app.models.system_metric import SystemMetric

from app.schemas.evidence import EvidenceCreate


# ============================================================
# Database Timeout Keywords
# ============================================================

DATABASE_TIMEOUT_KEYWORDS = (
    "timeout",
    "timed out",
    "queuepool",
    "database timeout",
    "db timeout",
    "connection timeout",
    "connection pool",
)


# ============================================================
# Metrics Correlation Window Buffer
# ============================================================
#
# Fluent Bit pushes metrics on its own independent interval
# (separate from log events). A correlation group's
# first_seen/last_seen window can be a single instant
# (when the group has only one log), so without a buffer,
# metrics almost never fall inside the window.
#
# TODO: tune this once the exact Fluent Bit metrics push
# interval (custom.conf) is confirmed. Currently set to a
# safe default.

METRICS_WINDOW_BUFFER_MINUTES = 3


# ============================================================
# Get Logs For Correlation Group
# ============================================================

def get_logs_for_group(
    db: Session,
    group_id: UUID,
):
    """
    Get all real logs belonging to a correlation group.
    """

    return (
        db.query(LogEvent)
        .filter(
            LogEvent.correlation_group_id == group_id
        )
        .order_by(
            LogEvent.timestamp.asc()
        )
        .all()
    )


# ============================================================
# Get Log Occurrence Count
# ============================================================

def get_log_occurrence_count(
    log: LogEvent,
) -> int:
    """
    Return the actual number of occurrences represented
    by a LogEvent.

    If occurrence_count is NULL or 0,
    treat the log as one occurrence.
    """

    return max(
        log.occurrence_count or 1,
        1,
    )


# ============================================================
# Calculate Database Timeout Count
# ============================================================

def calculate_database_timeout_count(
    logs: list[LogEvent],
) -> int:
    """
    Count actual occurrences of database timeout /
    connection-pool related problems from real logs.
    """

    count = 0

    for log in logs:

        message = (
            log.message or ""
        ).lower()

        if any(
            keyword in message
            for keyword in DATABASE_TIMEOUT_KEYWORDS
        ):
            count += get_log_occurrence_count(log)

    return count


# ============================================================
# Combine Logs
# ============================================================

def combine_logs(
    logs: list[LogEvent],
) -> str:
    """
    Convert real LogEvent records into one text block
    for Evidence and later LLM analysis.
    """

    combined = []

    for log in logs:

        occurrences = get_log_occurrence_count(log)

        timestamp = log.timestamp

        level = (
            log.level.upper()
            if log.level
            else "UNKNOWN"
        )

        message = log.message or ""

        combined.append(
            f"[{timestamp}] "
            f"[{level}] "
            f"{message} "
            f"(occurrences: {occurrences})"
        )

    return "\n".join(combined)


# ============================================================
# Get Metrics For Correlation Group
# ============================================================

def get_metrics_for_group(db: Session, group: CorrelationGroup):
    query = (
        db.query(SystemMetric)
        .filter(
            SystemMetric.client_id == group.client_id,
            SystemMetric.server_id == group.server_id,
            # application_id filter HATAYA - CPU/Memory/Disk server-wide hain,
            # kisi ek app ke naam se nahi. Isliye har app ki Evidence ko
            # wahi server-level metrics milne chahiye.
        )
    )

    # ------------------------------------------------------
    # Buffer the window on both sides.
    #
    # Fluent Bit pushes metrics on its own independent
    # interval, separate from log events. When a correlation
    # group has only one log, first_seen == last_seen, which
    # would otherwise create a zero-width window that almost
    # never matches any metric row. The buffer widens the
    # window so nearby metrics are still picked up.
    # ------------------------------------------------------

    buffer = timedelta(minutes=METRICS_WINDOW_BUFFER_MINUTES)

    if group.first_seen is not None:
        query = query.filter(
            SystemMetric.timestamp >= group.first_seen - buffer
        )

    if group.last_seen is not None:
        query = query.filter(
            SystemMetric.timestamp <= group.last_seen + buffer
        )

    return query.order_by(SystemMetric.timestamp.asc()).all()

# ============================================================
# Aggregate System Metrics
# ============================================================

def aggregate_system_metrics(
    db: Session,
    group: CorrelationGroup,
):
    """
    Aggregate separate SystemMetric rows into one snapshot.

    Fluent Bit sends metrics independently:

        CPU    -> SystemMetric row
        Memory -> SystemMetric row
        Disk   -> SystemMetric row

    This function takes the latest non-null value of each
    metric from the correlation group's real time window.

    Example:

        Row 1 -> cpu=96.9, memory=None
        Row 2 -> cpu=None, memory=97.8
        Row 3 -> cpu=99.3, memory=None

    Result:

        {
            "cpu_usage": 99.3,
            "memory_usage": 97.8,
            ...
        }
    """

    metrics = get_metrics_for_group(
        db=db,
        group=group,
    )

    result = {
        "cpu_usage": None,
        "memory_usage": None,
        "disk_usage": None,
        "disk_io_wait": None,
        "api_latency": None,
        "http_5xx_count": None,
        "http_4xx_count": None,
        "request_per_second": None,
        "request_count": None,
    }

    if not metrics:
        return result

    # --------------------------------------------------------
    # Metrics are ordered ASC.
    #
    # We iterate from newest -> oldest so the first non-null
    # value for each field is the latest value.
    # --------------------------------------------------------

    for metric in reversed(metrics):

        if (
            result["cpu_usage"] is None
            and metric.cpu_usage is not None
        ):
            result["cpu_usage"] = metric.cpu_usage

        if (
            result["memory_usage"] is None
            and metric.memory_usage is not None
        ):
            result["memory_usage"] = metric.memory_usage

        if (
            result["disk_usage"] is None
            and metric.disk_usage is not None
        ):
            result["disk_usage"] = metric.disk_usage

        if (
            result["disk_io_wait"] is None
            and metric.disk_io_wait is not None
        ):
            result["disk_io_wait"] = metric.disk_io_wait

        if (
            result["api_latency"] is None
            and metric.api_latency is not None
        ):
            result["api_latency"] = metric.api_latency

        if (
            result["http_5xx_count"] is None
            and metric.http_5xx_count is not None
        ):
            result["http_5xx_count"] = metric.http_5xx_count

        if (
            result["http_4xx_count"] is None
            and metric.http_4xx_count is not None
        ):
            result["http_4xx_count"] = metric.http_4xx_count

        if (
            result["request_per_second"] is None
            and metric.request_per_second is not None
        ):
            result["request_per_second"] = (
                metric.request_per_second
            )

        if (
            result["request_count"] is None
            and metric.request_count is not None
        ):
            result["request_count"] = metric.request_count

        # ----------------------------------------------------
        # Stop once every available metric has been found.
        # ----------------------------------------------------

        if all(
            value is not None
            for value in result.values()
        ):
            break

    return result


# ============================================================
# Build Evidence Data From Correlation Group
# ============================================================

def build_evidence_from_group(
    db: Session,
    group: CorrelationGroup,
):
    """
    Build Evidence entirely from REAL database data.

    Flow:

        Fluent Bit Logs
              ↓
          LogEvent
              ↓
        CorrelationGroup
              ↓
        Fluent Bit Metrics
              ↓
        SystemMetric
              ↓
        Evidence
    """

    # ========================================================
    # 1. Get REAL Logs
    # ========================================================

    logs = get_logs_for_group(
        db=db,
        group_id=group.id,
    )

    if not logs:
        return None

    # ========================================================
    # 2. Calculate Real Log Counts
    # ========================================================

    log_count = 0
    error_count = 0
    warning_count = 0

    for log in logs:

        occurrences = get_log_occurrence_count(
            log
        )

        # Total real occurrences
        log_count += occurrences

        level = (
            log.level.upper()
            if log.level
            else ""
        )

        # Real ERROR occurrences
        if level == "ERROR":

            error_count += occurrences

        # Real WARNING occurrences
        if level in (
            "WARNING",
            "WARN",
        ):

            warning_count += occurrences

    # ========================================================
    # 3. Real Time Range
    # ========================================================

    timestamps = [
        log.timestamp
        for log in logs
        if log.timestamp is not None
    ]

    first_seen = (
        min(timestamps)
        if timestamps
        else group.first_seen
    )

    last_seen = (
        max(timestamps)
        if timestamps
        else group.last_seen
    )

    # ========================================================
    # 4. Real Error Rate
    # ========================================================

    error_rate = (
        error_count / log_count
        if log_count > 0
        else 0.0
    )

    # ========================================================
    # 5. Real Database Timeout Count
    # ========================================================

    database_timeout_count = (
        calculate_database_timeout_count(
            logs
        )
    )

    # ========================================================
    # 6. Combine REAL Logs
    # ========================================================

    combined_logs = combine_logs(
        logs
    )

    # ========================================================
    # 7. Application Information
    # ========================================================

    application = db.get(
        Application,
        group.application_id,
    )

    service_name = None
    environment = None

    if application is not None:

        service_name = application.name

        # Current Application model does not
        # contain environment.
        environment = None

    # ========================================================
    # 8. Get REAL System Metrics
    # ========================================================

    metric_data = aggregate_system_metrics(
        db=db,
        group=group,
    )

    # ========================================================
    # 9. Build Final Evidence Data
    # ========================================================

    return {

        # ====================================================
        # Incident
        # ====================================================

        "incident_id": None,

        # ====================================================
        # REAL Log Evidence
        # ====================================================

        "log_count": log_count,

        "error_count": error_count,

        "warning_count": warning_count,

        "first_seen": first_seen,

        "last_seen": last_seen,

        "error_rate": error_rate,

        "database_timeout_count": (
            database_timeout_count
        ),

        "logs": combined_logs,

        # ====================================================
        # Application
        # ====================================================

        "service_name": service_name,

        "environment": environment,

        # ====================================================
        # REAL Infrastructure Metrics
        # ====================================================

        "cpu_usage": metric_data[
            "cpu_usage"
        ],

        "memory_usage": metric_data[
            "memory_usage"
        ],

        "disk_usage": metric_data[
            "disk_usage"
        ],

        "disk_io_wait": metric_data[
            "disk_io_wait"
        ],

        # ====================================================
        # REAL Network / API Metrics
        # ====================================================

        "api_latency": metric_data[
            "api_latency"
        ],

        # Not available in SystemMetric yet
        "network_latency": None,

        # Not available in SystemMetric yet
        "packet_loss": None,

        "request_per_second": metric_data[
            "request_per_second"
        ],

        # ====================================================
        # REAL Application Metrics
        # ====================================================

        "http_5xx_count": metric_data[
            "http_5xx_count"
        ],

        "http_4xx_count": metric_data[
            "http_4xx_count"
        ],

        # These fields are not currently present
        # in SystemMetric.
        "restart_count": None,

        "active_containers": None,

        "pod_restart_count": None,

        "deployment_changed": None,

        # ====================================================
        # Database Metrics
        # ====================================================

        # db_connections does not currently exist
        # in SystemMetric.
        "db_connections": None,

        # ====================================================
        # Security Metrics
        # ====================================================

        "failed_login_attempts": None,

        "ssl_certificate_days_left": None,
    }


# ============================================================
# Create Evidence From Correlation Group
# ============================================================
# ============================================================
# Create Evidence From Correlation Group
# ============================================================

def create_evidence_from_group(
    db: Session,
    group: CorrelationGroup,
):
    """
    Create Evidence directly from a CorrelationGroup.

    Flow:

        CorrelationGroup
              ↓
        REAL LogEvents
              +
        REAL SystemMetrics
              +
        Application metadata
              ↓
           Evidence

    Incident is NOT required at this stage.
    Incident will be created AFTER Evidence.
    """

    # ========================================================
    # 1. Build REAL Evidence from CorrelationGroup
    # ========================================================

    evidence_data = build_evidence_from_group(
        db=db,
        group=group,
    )

    if evidence_data is None:
        return None

    # ========================================================
    # 2. Evidence must initially have NO incident
    # ========================================================

    evidence_data["incident_id"] = None

    # ========================================================
    # 3. Create Evidence
    # ========================================================

    evidence = Evidence(
        **evidence_data
    )

    db.add(evidence)

    db.flush()

    return evidence

# ============================================================
# Manual Evidence Creation
# ============================================================

def create_evidence(
    db: Session,
    evidence_data: EvidenceCreate,
):
    """
    Manual evidence creation.

    Kept for compatibility with the existing API.

    Automatic monitoring flow must use:

        create_evidence_from_group()
    """

    incident = db.get(
        Incident,
        evidence_data.incident_id,
    )

    if incident is None:
        return None

    # ========================================================
    # Prevent Duplicate Evidence
    # ========================================================

    existing = (
        db.query(Evidence)
        .filter(
            Evidence.incident_id
            == evidence_data.incident_id
        )
        .first()
    )

    if existing is not None:
        return existing

    # ========================================================
    # Create Evidence
    # ========================================================

    evidence = Evidence(
        **evidence_data.model_dump()
    )

    db.add(evidence)

    db.commit()

    db.refresh(evidence)

    return evidence


# ============================================================
# Get Evidence By Incident
# ============================================================

def get_evidence_by_incident(db: Session, incident_id: UUID):
    return (
        db.query(Evidence)
        .filter(Evidence.incident_id == incident_id)
        .order_by(Evidence.created_at.desc())
        .first()
    )