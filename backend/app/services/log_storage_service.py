from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from app.models.log_event import LogEvent

# from app.core.config import (DUPLICATE_LOG_WINDOW_MINUTES,)
from app.core.config import settings


def get_log_by_fingerprint(
    db: Session,
    *,
    client_id,
    server_id,
    application_id,
    fingerprint: str,
    current_timestamp,
):
    """
    Find the latest matching event only if it falls
    inside the configured duplicate window.
    """

    window_start = (
        current_timestamp
        - timedelta(
            minutes=settings.DUPLICATE_LOG_WINDOW_MINUTES
        )
    )

    return (
        db.query(LogEvent)
        .filter(
            LogEvent.client_id == client_id,
            LogEvent.server_id == server_id,
            LogEvent.application_id == application_id,
            LogEvent.fingerprint == fingerprint,

            # Only treat it as duplicate if it was
            # seen recently.
            LogEvent.last_seen >= window_start,
        )
        .order_by(
            LogEvent.last_seen.desc()
        )
        .first()
    )


def update_duplicate_log(
    db: Session,
    *,
    existing_log: LogEvent,
    timestamp,
):
    """
    Update an existing event inside the deduplication window.
    """

    existing_log.occurrence_count += 1

    existing_log.last_seen = timestamp

    existing_log.timestamp = timestamp

    db.commit()

    db.refresh(existing_log)

    return existing_log


def save_log(
    db: Session,
    *,
    client_id,
    server_id,
    application_id,
    level,
    message,
    timestamp,
    fingerprint,
):
    """
    Create a new log event.
    """

    log = LogEvent(
        client_id=client_id,
        server_id=server_id,
        application_id=application_id,
        level=level,
        message=message,
        timestamp=timestamp,
        fingerprint=fingerprint,
        occurrence_count=1,
        first_seen=timestamp,
        last_seen=timestamp,
        status="PENDING",
    )

    db.add(log)

    db.commit()

    db.refresh(log)

    return log