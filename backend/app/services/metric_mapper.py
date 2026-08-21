from datetime import datetime

from app.schemas.metric_ingest import MetricIngestRequest


def map_fluentbit_metric(raw: dict) -> MetricIngestRequest:
    """
    Convert Fluent Bit / container collector metrics
    into MetricIngestRequest.

    Supports both:
    1. Normalized fields:
       cpu_usage, memory_usage, disk_usage

    2. Fluent Bit raw fields:
       cpu_p, Mem.total, Mem.used, etc.
    """

    # ==========================================================
    # CPU
    # ==========================================================

    cpu_usage = raw.get("cpu_usage")

    if cpu_usage is None:
        cpu_usage = raw.get("cpu_p")

    # ==========================================================
    # MEMORY
    # ==========================================================

    memory_usage = raw.get("memory_usage")

    if memory_usage is None:
        if raw.get("Mem.total") and raw.get("Mem.used") is not None:
            memory_usage = round(
                (raw["Mem.used"] / raw["Mem.total"]) * 100,
                2,
            )

    # ==========================================================
    # DISK
    # ==========================================================

    disk_usage = raw.get("disk_usage")

    if disk_usage is None:
        disk_usage = raw.get("disk_used_percent")

    # ==========================================================
    # TIMESTAMP
    # ==========================================================

    if raw.get("timestamp"):
        timestamp = raw["timestamp"]

    elif raw.get("date"):
        timestamp = datetime.fromtimestamp(raw["date"])

    else:
        timestamp = datetime.utcnow()

    # ==========================================================
    # BUILD METRIC REQUEST
    # ==========================================================

    return MetricIngestRequest(
        api_key=raw.get("api_key"),
        host=raw.get("host"),
        container_name=raw.get("container_name"),

        timestamp=timestamp,

        cpu_usage=cpu_usage,
        memory_usage=memory_usage,

        disk_usage=disk_usage,
        disk_io_wait=raw.get("disk_io_wait"),

        api_latency=raw.get("api_latency"),
        http_5xx_count=raw.get("http_5xx_count"),
        http_4xx_count=raw.get("http_4xx_count"),
        request_per_second=raw.get("request_per_second"),
        request_count=raw.get("request_count"),

        deployment_changed=raw.get("deployment_changed"),
    )
