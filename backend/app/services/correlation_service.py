from datetime import timedelta
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.log_event import LogEvent
from app.models.correlation_group import CorrelationGroup
from app.models.incident import Incident

from app.models.enums import StatusEnum
# ^ FIX: needed so OPEN_INCIDENT_STATUSES below uses the actual
#   Incident.status enum values instead of hand-typed strings.
#   The DB enum `statusenum` only defines OPEN / IN_PROGRESS /
#   RESOLVED / CLOSED — there is no "INVESTIGATING" value, so a
#   raw string "INVESTIGATING" here caused every
#   Incident.status.in_(...) query to fail with:
#     psycopg2.errors.InvalidTextRepresentation:
#     invalid input value for enum statusenum: "INVESTIGATING"
#   which in turn made correlate_log() blow up for any
#   application that already had an open incident, so no
#   CorrelationGroup (and therefore no Incident) could ever be
#   created for those logs.

from app.monitoring.correlation_rules import (
    should_correlate,
    CORRELATION_TIME_WINDOW_SECONDS,
)
# ^ requires exporting CORRELATION_TIME_WINDOW_SECONDS from
#   correlation_rules.py (it's already a module-level constant
#   there, so no change needed in that file besides the value).

# NOTE: the window constant now lives in correlation_rules.py only
# (single source of truth) — it was previously duplicated here as
# CORRELATION_WINDOW_SECONDS = 60, which risked the two values
# drifting apart if one was changed without the other.

# Statuses that mean "this incident is still ongoing" — a group
# linked to an incident in one of these states should keep
# absorbing new logs for the same application, no matter how much
# time has passed since last_seen. Only once an incident leaves
# this set (i.e. RESOLVED) should the next log start a fresh one.
#
# FIX: was ("OPEN", "INVESTIGATING") — "INVESTIGATING" does not
# exist in StatusEnum / the Postgres enum. The actual "still being
# worked on" value is IN_PROGRESS.
OPEN_INCIDENT_STATUSES = (
    StatusEnum.OPEN,
    StatusEnum.IN_PROGRESS,
)


def get_active_correlation_group(
    db: Session,
    client_id: UUID,
    server_id: UUID,
    application_id: UUID,
    timestamp,
):
    """
    Tier 1: tight rolling window.

    Groups a burst of closely-spaced logs (within
    CORRELATION_TIME_WINDOW_SECONDS of each other) into the same
    correlation group, same as before.
    """

    window_start = (
        timestamp
        - timedelta(
            seconds=CORRELATION_TIME_WINDOW_SECONDS
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


def get_group_for_open_incident(
    db: Session,
    client_id: UUID,
    server_id: UUID,
    application_id: UUID,
):
    """
    Tier 2: still-open incident, regardless of time gap.

    If the tight window above finds nothing, check whether this
    application already has an incident that is still OPEN or
    IN_PROGRESS (i.e. nobody has resolved it yet). If so, reuse
    the correlation group linked to that incident instead of
    starting a brand new one — this is what prevents a single
    ongoing problem from spawning a new incident every time the
    gap between error occurrences exceeds the short window.
    """

    return (
        db.query(CorrelationGroup)
        .join(
            Incident,
            CorrelationGroup.incident_id == Incident.id,
        )
        .filter(
            CorrelationGroup.client_id == client_id,
            CorrelationGroup.server_id == server_id,
            CorrelationGroup.application_id == application_id,
            Incident.status.in_(OPEN_INCIDENT_STATUSES),
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

    # last_seen only moves forward — a Tier 2 reattachment can
    # arrive with a timestamp close to "now" while the group's
    # own last_seen is old, so this keeps the rolling window
    # (Tier 1) useful again for whatever comes next.
    if group.last_seen is None or log.timestamp > group.last_seen:
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
    # Tier 1: candidate group within the tight rolling window
    # ========================================================

    candidate_group = get_active_correlation_group(
        db=db,
        client_id=log.client_id,
        server_id=log.server_id,
        application_id=log.application_id,
        timestamp=log.timestamp,
    )

    if candidate_group is not None and should_correlate(
        existing_group=candidate_group,
        log=log,
    ):
        return attach_log_to_group(
            db=db,
            log=log,
            group=candidate_group,
        )

    # ========================================================
    # Tier 2: no tight-window candidate — but this application
    # already has an incident that's still open. Reuse it rather
    # than opening a duplicate incident for the same ongoing
    # problem.
    # ========================================================

    open_incident_group = get_group_for_open_incident(
        db=db,
        client_id=log.client_id,
        server_id=log.server_id,
        application_id=log.application_id,
    )

    if open_incident_group is not None:
        return attach_log_to_group(
            db=db,
            log=log,
            group=open_incident_group,
        )

    # ========================================================
    # No existing group at all — genuinely new incident
    # ========================================================

    group = create_correlation_group(
        db=db,
        log=log,
    )

    log.correlation_group_id = group.id

    db.flush()

    return group