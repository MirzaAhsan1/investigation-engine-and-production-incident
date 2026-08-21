import uuid

from app.monitoring.log_fingerprint import (
    normalize_log_message,
    generate_log_fingerprint,
)


def test_normalize_log_message():

    message = (
        "Database timeout for user 123 "
        "from 192.168.1.50"
    )

    normalized = normalize_log_message(message)

    assert "<number>" in normalized
    assert "<ip>" in normalized


def test_same_event_generates_same_fingerprint():

    client_id = uuid.uuid4()
    server_id = uuid.uuid4()
    application_id = uuid.uuid4()

    message_1 = (
        "sqlalchemy.exc.TimeoutError: "
        "QueuePool limit of size 200 reached "
        "for connection 123"
    )

    message_2 = (
        "sqlalchemy.exc.TimeoutError: "
        "QueuePool limit of size 200 reached "
        "for connection 456"
    )

    fingerprint_1 = generate_log_fingerprint(
        client_id=client_id,
        server_id=server_id,
        application_id=application_id,
        level="ERROR",
        message=message_1,
    )

    fingerprint_2 = generate_log_fingerprint(
        client_id=client_id,
        server_id=server_id,
        application_id=application_id,
        level="ERROR",
        message=message_2,
    )

    assert fingerprint_1 == fingerprint_2


def test_different_level_generates_different_fingerprint():

    client_id = uuid.uuid4()
    server_id = uuid.uuid4()
    application_id = uuid.uuid4()

    message = "Database connection timeout"

    error_fingerprint = generate_log_fingerprint(
        client_id=client_id,
        server_id=server_id,
        application_id=application_id,
        level="ERROR",
        message=message,
    )

    warning_fingerprint = generate_log_fingerprint(
        client_id=client_id,
        server_id=server_id,
        application_id=application_id,
        level="WARNING",
        message=message,
    )

    assert error_fingerprint != warning_fingerprint