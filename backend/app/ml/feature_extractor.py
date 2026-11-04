from app.models.evidence import Evidence


FEATURE_COLUMNS = [
    "log_count",
    "error_count",
    "warning_count",
    "error_rate",
    "database_timeout_count",
    "cpu_usage",
    "memory_usage",
    "disk_usage",
    "disk_io_wait",
    "api_latency",
    "http_4xx_count",
    "http_5xx_count",
    "request_per_second",
    "active_containers",
    "deployment_changed",
    "failed_login_attempts",
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
        safe_value(evidence.log_count),
        safe_value(evidence.error_count),
        safe_value(evidence.warning_count),
        safe_value(evidence.error_rate),
        safe_value(evidence.database_timeout_count),
        safe_value(evidence.cpu_usage),
        safe_value(evidence.memory_usage),
        safe_value(evidence.disk_usage),
        safe_value(evidence.disk_io_wait),
        safe_value(evidence.api_latency),
        safe_value(evidence.http_4xx_count),
        safe_value(evidence.http_5xx_count),
        safe_value(evidence.request_per_second),
        safe_value(evidence.active_containers),
        safe_value(evidence.deployment_changed),
        safe_value(evidence.failed_login_attempts),
    ]

    if len(features) != len(FEATURE_COLUMNS):
        raise ValueError(
            f"Feature count mismatch: "
            f"{len(features)} values generated, "
            f"but model expects "
            f"{len(FEATURE_COLUMNS)} features."
        )

    return features