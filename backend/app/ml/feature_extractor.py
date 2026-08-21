from app.models.evidence import Evidence


FEATURE_COLUMNS = [
    "cpu_usage",
    "memory_usage",
    "disk_usage",
    "disk_io_wait",
    "api_latency",
    "http_5xx_count",
    "http_4xx_count",
    "request_per_second",
    "error_rate",
    "db_connections",
    "failed_login_attempts",
    "packet_loss",
    "network_latency",
    "restart_count",
    "active_containers",
    "deployment_changed",
    "ssl_certificate_days_left",
]


MISSING_VALUE_SENTINEL = -1.0


def safe_value(
    value,
    default=MISSING_VALUE_SENTINEL,
):
    """
    Keep missing evidence explicit.

    We do NOT convert missing metrics to 0 because
    zero and missing mean different things.
    """

    if value is None:
        return default

    if isinstance(value, bool):
        return int(value)

    return value


def extract_features(
    evidence: Evidence,
) -> list:

    features = [

        # ======================================================
        # Infrastructure
        # ======================================================

        safe_value(evidence.cpu_usage),
        safe_value(evidence.memory_usage),
        safe_value(evidence.disk_usage),
        safe_value(evidence.disk_io_wait),

        # ======================================================
        # API / HTTP
        # ======================================================

        safe_value(evidence.api_latency),
        safe_value(evidence.http_5xx_count),
        safe_value(evidence.http_4xx_count),
        safe_value(evidence.request_per_second),

        # ======================================================
        # Application
        # ======================================================

        safe_value(evidence.error_rate),

        # ======================================================
        # Database
        # ======================================================

        safe_value(evidence.db_connections),

        # ======================================================
        # Security
        # ======================================================

        safe_value(evidence.failed_login_attempts),

        # ======================================================
        # Network
        # ======================================================

        safe_value(evidence.packet_loss),
        safe_value(evidence.network_latency),

        # ======================================================
        # Runtime / Deployment
        # ======================================================

        safe_value(evidence.restart_count),
        safe_value(evidence.active_containers),
        safe_value(evidence.deployment_changed),

        # ======================================================
        # SSL
        # ======================================================

        safe_value(evidence.ssl_certificate_days_left),
    ]

    if len(features) != len(FEATURE_COLUMNS):
        raise ValueError(
            f"Feature count mismatch: "
            f"{len(features)} values generated, "
            f"but model expects "
            f"{len(FEATURE_COLUMNS)} features."
        )

    return features