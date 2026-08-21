from datetime import datetime
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.system_metric import SystemMetric


# ==========================================================
# Get Latest Metric
# ==========================================================

def get_latest_metric(
    db: Session,
    client_id: UUID,
    server_id: UUID | None = None,
    application_id: UUID | None = None,
):
    """
    Get the latest system metric for a client.

    Optional filters:
        server_id
        application_id
    """

    query = (
        db.query(SystemMetric)
        .filter(
            SystemMetric.client_id == client_id
        )
    )

    if server_id is not None:
        query = query.filter(
            SystemMetric.server_id == server_id
        )

    if application_id is not None:
        query = query.filter(
            SystemMetric.application_id == application_id
        )

    return (
        query
        .order_by(
            SystemMetric.timestamp.desc()
        )
        .first()
    )


# ==========================================================
# Get Metrics
# ==========================================================

def get_metrics(
    db: Session,
    client_id: UUID,
    server_id: UUID | None = None,
    application_id: UUID | None = None,
    start_time: datetime | None = None,
    end_time: datetime | None = None,
    limit: int = 100,
):
    """
    Get system metrics belonging to a client.

    Optional filters:
        server_id
        application_id
        start_time
        end_time
    """

    query = (
        db.query(SystemMetric)
        .filter(
            SystemMetric.client_id == client_id
        )
    )

    # ------------------------------------------------------
    # Server filter
    # ------------------------------------------------------

    if server_id is not None:
        query = query.filter(
            SystemMetric.server_id == server_id
        )

    # ------------------------------------------------------
    # Application filter
    # ------------------------------------------------------

    if application_id is not None:
        query = query.filter(
            SystemMetric.application_id == application_id
        )

    # ------------------------------------------------------
    # Start time
    # ------------------------------------------------------

    if start_time is not None:
        query = query.filter(
            SystemMetric.timestamp >= start_time
        )

    # ------------------------------------------------------
    # End time
    # ------------------------------------------------------

    if end_time is not None:
        query = query.filter(
            SystemMetric.timestamp <= end_time
        )

    # ------------------------------------------------------
    # Return newest first
    # ------------------------------------------------------

    return (
        query
        .order_by(
            SystemMetric.timestamp.desc()
        )
        .limit(limit)
        .all()
    )