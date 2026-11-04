from uuid import UUID

from datetime import timedelta

from types import SimpleNamespace

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
# Failed Login Keywords
# ============================================================

FAILED_LOGIN_KEYWORDS = (
    "login failed",
    "failed login",
    "invalid credentials",
    "invalid password",
    "authentication failed",
    "auth failed",
    "unauthorized login attempt",
    "login attempt failed",
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
# Calculate Failed Login Attempts
# ============================================================

def calculate_failed_login_attempts(
    logs: list[LogEvent],
) -> int:
    """
    Count actual occurrences of failed-login / auth-failure
    events from a monitored application's real logs.

    NOTE: this tracks the MONITORED application's own auth
    failures (e.g. a brute-force attempt against a client's
    app) — it has nothing to do with APIRS's own dashboard
    login (app/services/auth_service.py).
    """

    count = 0

    for log in logs:

        message = (
            log.message or ""
        ).lower()

        if any(
            keyword in message
            for keyword in FAILED_LOGIN_KEYWORDS
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


def get_application_metrics_for_group(
    db: Session,
    group: CorrelationGroup,
):
    """
    active_containers / deployment_changed are per-application
    (unlike CPU/memory which are server-wide), so this query
    filters by application_id too — otherwise App A's container
    status could leak into App B's evidence just because they
    share a server.
    """

    if group.application_id is None:
        return []

    query = (
        db.query(SystemMetric)
        .filter(
            SystemMetric.client_id == group.client_id,
            SystemMetric.server_id == group.server_id,
            SystemMetric.application_id == group.application_id,
        )
    )

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

    active_containers / deployment_changed come from a
    SEPARATE, application-scoped query (see
    get_application_metrics_for_group) since — unlike
    CPU/memory/disk — they belong to one specific application,
    not the whole server.

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

    app_metrics = get_application_metrics_for_group(
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
        "active_containers": None,
        "deployment_changed": None,
    }

    if not metrics and not app_metrics:
        return result

    # --------------------------------------------------------
    # Server-wide metrics are ordered ASC.
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
        # Stop once every server-wide metric has been found.
        # (active_containers/deployment_changed are handled
        # separately below from the app-scoped query.)
        # ----------------------------------------------------

        if all(
            value is not None
            for key, value in result.items()
            if key not in (
                "active_containers",
                "deployment_changed",
            )
        ):
            break

    # --------------------------------------------------------
    # active_containers / deployment_changed — from the
    # application-scoped Coolify status rows only, so one
    # app's container status can never leak into another's.
    # --------------------------------------------------------

    for metric in reversed(app_metrics):

        if (
            result["active_containers"] is None
            and metric.active_containers is not None
        ):
            result["active_containers"] = (
                metric.active_containers
            )

        if (
            result["deployment_changed"] is None
            and metric.deployment_changed is not None
        ):
            result["deployment_changed"] = (
                metric.deployment_changed
            )

        if (
            result["active_containers"] is not None
            and result["deployment_changed"] is not None
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
    # 5b. Real Failed Login Attempts
    # ========================================================

    failed_login_attempts = (
        calculate_failed_login_attempts(
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

        # restart_count / pod_restart_count remain out of
        # scope for now (no k8s, and Coolify exposes no raw
        # restart counter) — always None until that's revisited.
        "restart_count": None,

        "active_containers": metric_data[
            "active_containers"
        ],

        "pod_restart_count": None,

        "deployment_changed": metric_data[
            "deployment_changed"
        ],

        # ====================================================
        # Database Metrics
        # ====================================================

        # db_connections does not currently exist
        # in SystemMetric.
        "db_connections": None,

        # ====================================================
        # Security Metrics
        # ====================================================

        "failed_login_attempts": failed_login_attempts,

        "ssl_certificate_days_left": None,
    }


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


# ============================================================
# Aggregate ALL Evidence For An Incident (incident-level view)
# ============================================================

RECENT_EVIDENCE_LOG_LIMIT = 10
LOG_TEXT_CHAR_CAP = 8000


def aggregate_incident_evidence(
    db: Session,
    incident_id: UUID,
):
    """
    Build ONE incident-level evidence view from ALL Evidence
    rows tied to this incident (across every CorrelationGroup
    that fed into it) — instead of only the latest snapshot.

    Used by both ML (ml_service.py) and LLM
    (investigation_pipeline.py) so they always see the SAME,
    complete picture of the incident's lifetime, not just its
    most recent burst.

    Strategy:
        - Counts (log_count, error_count, warning_count,
          database_timeout_count) are SUMMED across every
          Evidence row — cheap, always accurate, reflects the
          incident's full history.
        - error_rate is recomputed from the summed counts.
        - Metrics (cpu_usage, memory_usage, etc.) and metadata
          (service_name, environment) come from the LATEST row
          only — they represent current state, not something
          to sum/average.
        - Raw log text is combined from only the most recent
          RECENT_EVIDENCE_LOG_LIMIT rows, further capped at
          LOG_TEXT_CHAR_CAP characters, to keep prompts bounded
          for long-running incidents.

    Returns an Evidence-shaped object (SimpleNamespace) so
    downstream code (extract_features, build_prompt) can keep
    accessing fields via dot notation exactly as it does for a
    real Evidence row.
    """

    rows = (
        db.query(Evidence)
        .filter(
            Evidence.incident_id == incident_id
        )
        .order_by(
            Evidence.created_at.asc()
        )
        .all()
    )

    if not rows:
        return None

    # --------------------------------------------------------
    # Sum count-like fields across ALL rows
    # --------------------------------------------------------

    log_count = sum(r.log_count or 0 for r in rows)
    error_count = sum(r.error_count or 0 for r in rows)
    warning_count = sum(r.warning_count or 0 for r in rows)
    database_timeout_count = sum(
        r.database_timeout_count or 0 for r in rows
    )

    error_rate = (
        error_count / log_count
        if log_count > 0
        else 0.0
    )

    first_seen = min(
        (
            r.first_seen
            for r in rows
            if r.first_seen is not None
        ),
        default=None,
    )

    last_seen = max(
        (
            r.last_seen
            for r in rows
            if r.last_seen is not None
        ),
        default=None,
    )

    # --------------------------------------------------------
    # Latest row — for point-in-time metrics / metadata
    # --------------------------------------------------------

    latest = rows[-1]

    # --------------------------------------------------------
    # Combine raw log text — only the most recent N rows,
    # further capped by character count
    # --------------------------------------------------------

    recent_rows = rows[-RECENT_EVIDENCE_LOG_LIMIT:]

    combined_logs = "\n".join(
        r.logs for r in recent_rows if r.logs
    )

    if len(combined_logs) > LOG_TEXT_CHAR_CAP:
        combined_logs = (
            "...[earlier logs truncated]...\n"
            + combined_logs[-LOG_TEXT_CHAR_CAP:]
        )

    # --------------------------------------------------------
    # Return an Evidence-shaped object
    # --------------------------------------------------------

    return SimpleNamespace(
        incident_id=incident_id,

        log_count=log_count,
        error_count=error_count,
        warning_count=warning_count,
        first_seen=first_seen,
        last_seen=last_seen,
        error_rate=error_rate,
        database_timeout_count=database_timeout_count,
        logs=combined_logs,

        service_name=latest.service_name,
        environment=latest.environment,

        cpu_usage=latest.cpu_usage,
        memory_usage=latest.memory_usage,
        disk_usage=latest.disk_usage,
        disk_io_wait=latest.disk_io_wait,

        api_latency=latest.api_latency,
        network_latency=latest.network_latency,
        packet_loss=latest.packet_loss,
        request_per_second=latest.request_per_second,

        http_5xx_count=latest.http_5xx_count,
        http_4xx_count=latest.http_4xx_count,
        restart_count=latest.restart_count,
        active_containers=latest.active_containers,
        pod_restart_count=latest.pod_restart_count,
        deployment_changed=latest.deployment_changed,

        db_connections=latest.db_connections,

        failed_login_attempts=latest.failed_login_attempts,
        ssl_certificate_days_left=latest.ssl_certificate_days_left,
    )