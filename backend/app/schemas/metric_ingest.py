from datetime import datetime

from pydantic import BaseModel


class MetricIngestRequest(BaseModel):

    # ==========================================================
    # Authentication / Server Identification
    # ==========================================================

    api_key: str

    host: str

    # IMPORTANT:
    # Optional because CPU / Memory / Disk metrics
    # are server-wide metrics and do not belong to
    # a specific application/container.
    #
    # For application-specific metrics such as
    # Traefik/API metrics, this can be provided.
    container_name: str | None = None

    # ==========================================================
    # Metric Timestamp
    # ==========================================================

    timestamp: datetime

    # ==========================================================
    # Server-Level Infrastructure Metrics
    # ==========================================================

    cpu_usage: float | None = None

    memory_usage: float | None = None

    disk_usage: float | None = None

    disk_io_wait: float | None = None

    # ==========================================================
    # Application / HTTP Metrics
    # ==========================================================

    api_latency: float | None = None

    http_5xx_count: int | None = None

    http_4xx_count: int | None = None

    request_per_second: float | None = None

    request_count: int | None = None

    # ==========================================================
    # Deployment
    # ==========================================================

    deployment_changed: bool | None = None