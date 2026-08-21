from datetime import datetime, timedelta, timezone
from uuid import uuid4

import pytest

from app.models.log_event import LogEvent
from app.models.correlation_group import CorrelationGroup

from app.services.correlation_service import (
    correlate_log,
)


# ============================================================
# Helpers
# ============================================================

def create_log(
    client_id,
    server_id,
    application_id,
    timestamp,
    level="ERROR",
    message="Database connection timeout",
):
    """
    Create a LogEvent object without committing it.
    """

    return LogEvent(
        client_id=client_id,
        server_id=server_id,
        application_id=application_id,
        level=level,
        message=message,
        timestamp=timestamp,
    )


# ============================================================
# Test 1
# Same application + same time window
# should produce SAME correlation group
# ============================================================

def test_related_logs_go_to_same_group(db_session):

    client_id = uuid4()
    server_id = uuid4()
    application_id = uuid4()

    timestamp = datetime.now(
        timezone.utc
    )

    # ------------------------------------------
    # First log
    # ------------------------------------------

    log_1 = create_log(
        client_id=client_id,
        server_id=server_id,
        application_id=application_id,
        timestamp=timestamp,
        message="Database connection timeout",
    )

    db_session.add(log_1)
    db_session.flush()

    group_1 = correlate_log(
        db=db_session,
        log=log_1,
    )

    db_session.commit()

    # ------------------------------------------
    # Second related log
    # ------------------------------------------

    log_2 = create_log(
        client_id=client_id,
        server_id=server_id,
        application_id=application_id,
        timestamp=timestamp + timedelta(
            seconds=10
        ),
        message="Connection pool exhausted",
    )

    db_session.add(log_2)
    db_session.flush()

    group_2 = correlate_log(
        db=db_session,
        log=log_2,
    )

    db_session.commit()

    # ------------------------------------------
    # Assertions
    # ------------------------------------------

    assert group_1.id == group_2.id

    assert log_1.correlation_group_id == group_1.id

    assert log_2.correlation_group_id == group_1.id

    assert group_2.event_count == 2


# ============================================================
# Test 2
# Different application
# should produce DIFFERENT groups
# ============================================================

def test_different_application_creates_new_group(
    db_session,
):

    client_id = uuid4()
    server_id = uuid4()

    application_1 = uuid4()
    application_2 = uuid4()

    timestamp = datetime.now(
        timezone.utc
    )

    # ------------------------------------------
    # Application 1
    # ------------------------------------------

    log_1 = create_log(
        client_id=client_id,
        server_id=server_id,
        application_id=application_1,
        timestamp=timestamp,
        message="Database timeout",
    )

    db_session.add(log_1)
    db_session.flush()

    group_1 = correlate_log(
        db=db_session,
        log=log_1,
    )

    db_session.commit()

    # ------------------------------------------
    # Application 2
    # ------------------------------------------

    log_2 = create_log(
        client_id=client_id,
        server_id=server_id,
        application_id=application_2,
        timestamp=timestamp + timedelta(
            seconds=5
        ),
        message="Database timeout",
    )

    db_session.add(log_2)
    db_session.flush()

    group_2 = correlate_log(
        db=db_session,
        log=log_2,
    )

    db_session.commit()

    # ------------------------------------------
    # Assertions
    # ------------------------------------------

    assert group_1.id != group_2.id

    assert (
        log_1.correlation_group_id
        != log_2.correlation_group_id
    )

    assert group_1.event_count == 1

    assert group_2.event_count == 1


# ============================================================
# Test 3
# Same application but outside time window
# should create NEW group
# ============================================================

def test_expired_time_window_creates_new_group(
    db_session,
):

    client_id = uuid4()
    server_id = uuid4()
    application_id = uuid4()

    timestamp = datetime.now(
        timezone.utc
    )

    # ------------------------------------------
    # First log
    # ------------------------------------------

    log_1 = create_log(
        client_id=client_id,
        server_id=server_id,
        application_id=application_id,
        timestamp=timestamp,
        message="Database connection timeout",
    )

    db_session.add(log_1)
    db_session.flush()

    group_1 = correlate_log(
        db=db_session,
        log=log_1,
    )

    db_session.commit()

    # ------------------------------------------
    # Second log
    #
    # 60+ seconds later
    # ------------------------------------------

    log_2 = create_log(
        client_id=client_id,
        server_id=server_id,
        application_id=application_id,
        timestamp=timestamp + timedelta(
            seconds=120
        ),
        message="Database connection timeout",
    )

    db_session.add(log_2)
    db_session.flush()

    group_2 = correlate_log(
        db=db_session,
        log=log_2,
    )

    db_session.commit()

    # ------------------------------------------
    # Assertions
    # ------------------------------------------

    assert group_1.id != group_2.id

    assert group_1.event_count == 1

    assert group_2.event_count == 1


# ============================================================
# Test 4
# Multiple related logs
# should increment event_count
# ============================================================

def test_multiple_logs_increment_event_count(
    db_session,
):

    client_id = uuid4()
    server_id = uuid4()
    application_id = uuid4()

    timestamp = datetime.now(
        timezone.utc
    )

    messages = [
        "Database connection timeout",
        "Connection pool exhausted",
        "Database timeout",
        "API request timeout",
        "503 Service Unavailable",
    ]

    groups = []

    # ------------------------------------------
    # Send 5 related logs
    # ------------------------------------------

    for index, message in enumerate(
        messages
    ):

        log = create_log(
            client_id=client_id,
            server_id=server_id,
            application_id=application_id,
            timestamp=timestamp + timedelta(
                seconds=index * 5
            ),
            message=message,
        )

        db_session.add(log)
        db_session.flush()

        group = correlate_log(
            db=db_session,
            log=log,
        )

        groups.append(group)

    db_session.commit()

    # ------------------------------------------
    # All logs should belong to same group
    # ------------------------------------------

    first_group_id = groups[0].id

    for group in groups:

        assert group.id == first_group_id

    # ------------------------------------------
    # Event count should be 5
    # ------------------------------------------

    final_group = db_session.get(
        CorrelationGroup,
        first_group_id,
    )

    assert final_group.event_count == 5