from sqlalchemy.orm import Session

from app.models.system_metric import SystemMetric
from app.schemas.metric import MetricIngestRequest


def save_system_metric(
    db: Session,
    metric_data: MetricIngestRequest,
):
    """
    Store CPU and memory metrics received
    from Fluent Bit.
    """

    metric = SystemMetric(
        client_id=metric_data.client_id,
        server_id=metric_data.server_id,
        application_id=metric_data.application_id,
        timestamp=metric_data.timestamp,
        cpu_usage=metric_data.cpu_usage,
        memory_usage=metric_data.memory_usage,
    )

    db.add(metric)

    db.commit()

    db.refresh(metric)

    return metric