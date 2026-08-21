from datetime import timedelta
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.log_event import LogEvent
from app.models.correlation_group import CorrelationGroup

from app.monitoring.correlation_rules import (
    should_correlate,
)


CORRELATION_WINDOW_SECONDS = 60


def get_active_correlation_group(
    db: Session,
    client_id: UUID,
    server_id: UUID,
    application_id: UUID,
    timestamp,
):
    window_start = (
        timestamp
        - timedelta(
            seconds=CORRELATION_WINDOW_SECONDS
        )
    )

    return (
        db.query(CorrelationGroup)
        .filter(
            CorrelationGroup.client_id == client_id,
            CorrelationGroup.server_id == server_id,
            CorrelationGroup.application_id == application_id,
            CorrelationGroup.status == "OPEN",
            CorrelationGroup.last_seen >= window_start,
            CorrelationGroup.last_seen <= timestamp,
        )
        .order_by(
            CorrelationGroup.last_seen.desc()
        )
        .first()
    )


def create_correlation_group(
    db: Session,
    log: LogEvent,
):
    group = CorrelationGroup(
        client_id=log.client_id,
        server_id=log.server_id,
        application_id=log.application_id,

        first_seen=log.timestamp,
        last_seen=log.timestamp,

        event_count=1,

        status="OPEN",

        correlation_type="APPLICATION",
    )

    db.add(group)

    db.flush()

    return group


def attach_log_to_group(
    db: Session,
    log: LogEvent,
    group: CorrelationGroup,
):
    log.correlation_group_id = group.id

    group.last_seen = log.timestamp

    group.event_count = (
        group.event_count or 0
    ) + 1

    db.flush()

    return group


def correlate_log(
    db: Session,
    log: LogEvent,
):
    """
    Only handles correlation.

    This service does NOT create:
        - Incident
        - Evidence
        - Investigation
        - Actions
    """

    # ========================================================
    # Already correlated
    # ========================================================

    if log.correlation_group_id is not None:

        existing_group = db.get(
            CorrelationGroup,
            log.correlation_group_id,
        )

        if existing_group is not None:
            return existing_group

    # ========================================================
    # Find candidate group
    # ========================================================

    candidate_group = get_active_correlation_group(
        db=db,
        client_id=log.client_id,
        server_id=log.server_id,
        application_id=log.application_id,
        timestamp=log.timestamp,
    )

    # ========================================================
    # No existing group
    # ========================================================

    if candidate_group is None:

        group = create_correlation_group(
            db=db,
            log=log,
        )

        log.correlation_group_id = group.id

        db.flush()

        return group

    # ========================================================
    # Check correlation rules
    # ========================================================

    if should_correlate(
        existing_group=candidate_group,
        log=log,
    ):

        return attach_log_to_group(
            db=db,
            log=log,
            group=candidate_group,
        )

    # ========================================================
    # Doesn't belong to candidate
    # ========================================================

    group = create_correlation_group(
        db=db,
        log=log,
    )

    log.correlation_group_id = group.id

    db.flush()

    return group