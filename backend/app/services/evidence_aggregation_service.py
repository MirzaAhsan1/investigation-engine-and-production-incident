from uuid import UUID

from sqlalchemy.orm import Session

from app.models.application import Application
from app.models.correlation_group import CorrelationGroup
from app.models.evidence import Evidence
from app.models.incident import Incident
from app.models.log_event import LogEvent
from app.models.server import Server

from app.services.system_metrics_service import (
    aggregate_system_metrics,
)


# ============================================================
# Database Timeout Keywords
# ============================================================

DATABASE_TIMEOUT_KEYWORDS = (
    "timeout",
    "database timeout",
    "db timeout",
    "queuepool",
    "connection timeout",
    "database connection",
    "connection pool",
)


# ============================================================
# Database Timeout Detection
# ============================================================

def is_database_timeout(
    message: str,
) -> bool:

    message_lower = (
        message or ""
    ).lower()

    return any(
        keyword in message_lower
        for keyword in DATABASE_TIMEOUT_KEYWORDS
    )


# ============================================================
# Log Occurrence Count
# ============================================================

def get_log_occurrence_count(
    log: LogEvent,
) -> int:

    return max(
        log.occurrence_count or 1,
        1,
    )


# ============================================================
# Step 2
# Fetch All Related LogEvents
# ============================================================

def aggregate_group_logs(
    db: Session,
    group: CorrelationGroup,
):
    """
    Fetch and aggregate ALL LogEvents belonging
    to this CorrelationGroup.
    """

    logs = (
        db.query(LogEvent)
        .filter(
            LogEvent.correlation_group_id
            == group.id,
        )
        .order_by(
            LogEvent.timestamp.asc()
        )
        .all()
    )

    if not logs:

        return {
            "log_count": 0,
            "error_count": 0,
            "warning_count": 0,
            "first_seen": group.first_seen,
            "last_seen": group.last_seen,
            "error_rate": 0.0,
            "database_timeout_count": 0,
            "logs": "",
        }

    log_count = 0
    error_count = 0
    warning_count = 0
    database_timeout_count = 0

    combined_logs = []

    first_seen = None
    last_seen = None

    for log in logs:

        occurrences = (
            get_log_occurrence_count(log)
        )

        log_count += occurrences

        level = (
            log.level.upper()
            if log.level
            else "UNKNOWN"
        )

        if level == "ERROR":
            error_count += occurrences

        if level in (
            "WARNING",
            "WARN",
        ):
            warning_count += occurrences

        if is_database_timeout(
            log.message
        ):
            database_timeout_count += (
                occurrences
            )

        current_first_seen = (
            log.first_seen
            or log.timestamp
        )

        current_last_seen = (
            log.last_seen
            or log.timestamp
        )

        if current_first_seen is not None:

            if (
                first_seen is None
                or current_first_seen < first_seen
            ):
                first_seen = current_first_seen

        if current_last_seen is not None:

            if (
                last_seen is None
                or current_last_seen > last_seen
            ):
                last_seen = current_last_seen

        combined_logs.append(
            f"[{log.timestamp}] "
            f"[{level}] "
            f"{log.message or ''} "
            f"(occurrences: {occurrences})"
        )

    error_rate = (
        error_count / log_count
        if log_count > 0
        else 0.0
    )

    return {
        "log_count": log_count,
        "error_count": error_count,
        "warning_count": warning_count,
        "first_seen": first_seen,
        "last_seen": last_seen,
        "error_rate": error_rate,
        "database_timeout_count": (
            database_timeout_count
        ),
        "logs": "\n".join(
            combined_logs
        ),
    }


# ============================================================
# Step 3
# Collect Metrics Around Same Time Window
# ============================================================

def get_group_metrics(
    db: Session,
    group: CorrelationGroup,
):
    """
    Collect REAL metrics belonging to the same:

        client
        server
        application

    and the same correlation time window.
    """

    return aggregate_system_metrics(
        db=db,
        group=group,
    )


# ============================================================
# Step 4
# Collect Application / Container Metadata
# ============================================================

def get_application_metadata(
    db: Session,
    group: CorrelationGroup,
):
    """
    Get application/container metadata associated
    with the correlation group.
    """

    application = db.get(
        Application,
        group.application_id,
    )

    server = db.get(
        Server,
        group.server_id,
    )

    service_name = None
    environment = None

    if application is not None:
        service_name = application.name

    if server is not None:
        environment = server.environment

    return {
        "service_name": service_name,
        "environment": environment,
    }


# ============================================================
# Step 5
# Build Aggregated Evidence
# ============================================================

def build_evidence_from_group(
    db: Session,
    group: CorrelationGroup,
):
    """
    Build one aggregated Evidence object from one
    CorrelationGroup.

    Flow:

        CorrelationGroup
              |
              +---- LogEvents
              |
              +---- SystemMetrics
              |
              +---- Application
              |
              +---- Server
              |
              v
          Aggregated Evidence
    """

    # ========================================================
    # 1. Logs
    # ========================================================

    log_data = aggregate_group_logs(
        db=db,
        group=group,
    )

    # ========================================================
    # 2. Metrics
    # ========================================================

    metric_data = get_group_metrics(
        db=db,
        group=group,
    )

    # ========================================================
    # 3. Application / Container Metadata
    # ========================================================

    metadata = get_application_metadata(
        db=db,
        group=group,
    )

    # ========================================================
    # 4. Create One Aggregated Evidence Payload
    # ========================================================

    return {
        # ----------------------------------------------------
        # Correlation Group
        # ----------------------------------------------------

        "correlation_group_id": group.id,

        # ----------------------------------------------------
        # Incident
        #
        # At this stage incident does NOT exist yet.
        # ----------------------------------------------------

        "incident_id": None,

        # ----------------------------------------------------
        # Logs
        # ----------------------------------------------------

        "log_count": log_data[
            "log_count"
        ],

        "error_count": log_data[
            "error_count"
        ],

        "warning_count": log_data[
            "warning_count"
        ],

        "first_seen": log_data[
            "first_seen"
        ],

        "last_seen": log_data[
            "last_seen"
        ],

        "error_rate": log_data[
            "error_rate"
        ],

        "database_timeout_count": (
            log_data[
                "database_timeout_count"
            ]
        ),

        "logs": log_data[
            "logs"
        ],

        # ----------------------------------------------------
        # Application / Container
        # ----------------------------------------------------

        "service_name": metadata[
            "service_name"
        ],

        "environment": metadata[
            "environment"
        ],

        # ----------------------------------------------------
        # Infrastructure Metrics
        # ----------------------------------------------------

        "cpu_usage": metric_data.get(
            "cpu_usage"
        ),

        "memory_usage": metric_data.get(
            "memory_usage"
        ),

        "disk_usage": metric_data.get(
            "disk_usage"
        ),

        "disk_io_wait": metric_data.get(
            "disk_io_wait"
        ),

        # ----------------------------------------------------
        # Network / API Metrics
        # ----------------------------------------------------

        "api_latency": metric_data.get(
            "api_latency"
        ),

        "network_latency": metric_data.get(
            "network_latency"
        ),

        "packet_loss": metric_data.get(
            "packet_loss"
        ),

        "request_per_second": metric_data.get(
            "request_per_second"
        ),

        # ----------------------------------------------------
        # Application Metrics
        # ----------------------------------------------------

        "http_5xx_count": metric_data.get(
            "http_5xx_count"
        ),

        "http_4xx_count": metric_data.get(
            "http_4xx_count"
        ),

        "restart_count": metric_data.get(
            "restart_count"
        ),

        "active_containers": metric_data.get(
            "active_containers"
        ),

        "pod_restart_count": metric_data.get(
            "pod_restart_count"
        ),

        "deployment_changed": metric_data.get(
            "deployment_changed"
        ),

        # ----------------------------------------------------
        # Database Metrics
        # ----------------------------------------------------

        "db_connections": metric_data.get(
            "db_connections"
        ),

        # ----------------------------------------------------
        # Security Metrics
        # ----------------------------------------------------

        "failed_login_attempts": metric_data.get(
            "failed_login_attempts"
        ),

        "ssl_certificate_days_left": (
            metric_data.get(
                "ssl_certificate_days_left"
            )
        ),
    }


# ============================================================
# Create / Update Evidence From Correlation Group
# ============================================================

def create_or_update_evidence_from_group(
    db: Session,
    group: CorrelationGroup,
):
    """
    Create or update Evidence for a CorrelationGroup.

    IMPORTANT:

    Evidence is created BEFORE Incident.

    Therefore:

        correlation_group_id = group.id
        incident_id = None

    Initially.

    Later Incident creation will attach
    the incident_id to this Evidence.
    """

    # ========================================================
    # 1. Find Existing Evidence For This Group
    # ========================================================

    evidence = (
        db.query(Evidence)
        .filter(
            Evidence.correlation_group_id
            == group.id,
        )
        .first()
    )

    # ========================================================
    # 2. Build Fresh Aggregated Data
    # ========================================================

    evidence_data = build_evidence_from_group(
        db=db,
        group=group,
    )

    # ========================================================
    # 3. Create
    # ========================================================

    if evidence is None:

        evidence = Evidence(
            **evidence_data
        )

        db.add(evidence)

    # ========================================================
    # 4. Update
    # ========================================================

    else:

        for field, value in evidence_data.items():

            # Do not overwrite an existing
            # incident relationship here.
            if field == "incident_id":
                continue

            setattr(
                evidence,
                field,
                value,
            )

    # ========================================================
    # 5. Flush
    #
    # Do NOT commit here.
    #
    # The caller should commit the complete
    # CorrelationGroup -> Evidence -> Incident
    # transaction together.
    # ========================================================

    db.flush()

    return evidence


# ============================================================
# Attach Evidence To Incident
# ============================================================

def attach_evidence_to_incident(
    db: Session,
    evidence: Evidence,
    incident: Incident,
):
    """
    Connect already-created Evidence to its Incident.
    """

    evidence.incident_id = incident.id

    db.flush()

    return evidence


# ============================================================
# Get Evidence By Correlation Group
# ============================================================

def get_evidence_by_group(
    db: Session,
    group_id: UUID,
):
    return (
        db.query(Evidence)
        .filter(
            Evidence.correlation_group_id
            == group_id,
        )
        .first()
    )


# ============================================================
# Get Evidence By Incident
# ============================================================

def get_evidence_by_incident(
    db: Session,
    incident_id: UUID,
):
    return (
        db.query(Evidence)
        .filter(
            Evidence.incident_id
            == incident_id,
        )
        .first()
    )