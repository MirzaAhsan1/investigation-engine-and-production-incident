from sqlalchemy.orm import Session

from app.models.system_metric import SystemMetric
from app.schemas.metric_ingest import MetricIngestRequest

from app.services.client_service import (
    get_client_by_api_key,
)

from app.services.server_service import (
    get_server_by_host,
)

from app.services.application_service import (
    get_application_by_container,
)


def ingest_metric(
    db: Session,
    metric_data: MetricIngestRequest,
):
    """
    Ingest monitoring metrics.

    Server-level metrics:
        CPU
        Memory
        Disk
        Disk I/O

    Application-level metrics:
        API latency
        HTTP 4xx
        HTTP 5xx
        RPS
        Request count

    container_name is optional.

    If container_name is not provided:
        application_id = NULL

    If container_name is provided:
        application_id = resolved application ID
    """

    # ==========================================================
    # 1. Authenticate Client
    # ==========================================================

    client = get_client_by_api_key(
        db=db,
        api_key=metric_data.api_key,
    )

    if client is None:
        return {
            "status": "unauthorized",
            "reason": "Invalid monitoring API key",
        }

    # ==========================================================
    # 2. Resolve Server
    # ==========================================================

    server = get_server_by_host(
        db=db,
        client_id=client.id,
        host=metric_data.host,
    )

    if server is None:
        return {
            "status": "server_not_found",
            "reason": (
                f"Server '{metric_data.host}' "
                "is not registered for this client"
            ),
        }

    # ==========================================================
    # 3. Resolve Application ONLY if container_name exists
    # ==========================================================

    application = None

    container_name = getattr(
        metric_data,
        "container_name",
        None,
    )

    if container_name:

        application = get_application_by_container(
            db=db,
            server_id=server.id,
            container_name=container_name,
        )

        # ------------------------------------------------------
        # Container was explicitly provided but not registered
        # ------------------------------------------------------

        if application is None:
            return {
                "status": "application_not_found",
                "reason": (
                    f"Application/container "
                    f"'{container_name}' "
                    "is not registered on this server"
                ),
            }

    # ==========================================================
    # 4. Create System Metric
    # ==========================================================

    metric = SystemMetric(
        client_id=client.id,

        server_id=server.id,

        # Server-wide metrics:
        # application_id = NULL
        #
        # Application-specific metrics:
        # application_id = actual application ID
        application_id=(
            application.id
            if application is not None
            else None
        ),

        timestamp=metric_data.timestamp,

        # ======================================================
        # Infrastructure Metrics
        # ======================================================

        cpu_usage=metric_data.cpu_usage,

        memory_usage=metric_data.memory_usage,

        disk_usage=metric_data.disk_usage,

        disk_io_wait=metric_data.disk_io_wait,

        # ======================================================
        # Application / HTTP Metrics
        # ======================================================

        api_latency=metric_data.api_latency,

        http_5xx_count=metric_data.http_5xx_count,

        http_4xx_count=metric_data.http_4xx_count,

        request_per_second=(
            metric_data.request_per_second
        ),

        request_count=(
            metric_data.request_count
        ),
    )

    # ==========================================================
    # 5. Save
    # ==========================================================

    db.add(metric)

    db.commit()

    db.refresh(metric)

    # ==========================================================
    # 6. Response
    # ==========================================================

    return {
        "status": "success",

        "metric_id": str(
            metric.id
        ),

        "client_id": str(
            metric.client_id
        ),

        "server_id": str(
            metric.server_id
        ),

        "application_id": (
            str(metric.application_id)
            if metric.application_id
            else None
        ),

        "timestamp": metric.timestamp,

        "cpu_usage": metric.cpu_usage,

        "memory_usage": metric.memory_usage,

        "disk_usage": metric.disk_usage,

        "disk_io_wait": metric.disk_io_wait,

        "api_latency": metric.api_latency,

        "http_5xx_count": (
            metric.http_5xx_count
        ),

        "http_4xx_count": (
            metric.http_4xx_count
        ),

        "request_per_second": (
            metric.request_per_second
        ),

        "request_count": (
            metric.request_count
        ),
    }