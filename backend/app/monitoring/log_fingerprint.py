import hashlib
import re


def normalize_log_message(message: str) -> str:
    """
    Normalize a log message before generating its fingerprint.

    Dynamic values such as UUIDs, IP addresses, numbers and
    timestamps are replaced so that the same type of event
    can produce the same fingerprint.
    """

    if not message:
        return ""

    normalized = message.strip().lower()

    # -----------------------------------------
    # Remove timestamps
    # -----------------------------------------

    normalized = re.sub(
        r"\b\d{4}-\d{2}-\d{2}[t\s]\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:z|[+-]\d{2}:\d{2})?\b",
        "<timestamp>",
        normalized,
    )

    # -----------------------------------------
    # Replace UUIDs
    # -----------------------------------------

    normalized = re.sub(
        r"\b[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-"
        r"[89ab][0-9a-f]{3}-[0-9a-f]{12}\b",
        "<uuid>",
        normalized,
    )

    # -----------------------------------------
    # Replace IPv4 addresses
    # -----------------------------------------

    normalized = re.sub(
        r"\b(?:\d{1,3}\.){3}\d{1,3}\b",
        "<ip>",
        normalized,
    )

    # -----------------------------------------
    # Replace hexadecimal values
    # -----------------------------------------

    normalized = re.sub(
        r"\b0x[0-9a-f]+\b",
        "<hex>",
        normalized,
    )

    # -----------------------------------------
    # Replace standalone numbers
    # -----------------------------------------

    normalized = re.sub(
        r"\b\d+\b",
        "<number>",
        normalized,
    )

    # -----------------------------------------
    # Normalize whitespace
    # -----------------------------------------

    normalized = re.sub(
        r"\s+",
        " ",
        normalized,
    )

    return normalized.strip()


def generate_log_fingerprint(
    *,
    client_id,
    server_id,
    application_id,
    level: str,
    message: str,
) -> str:
    """
    Generate a stable SHA-256 fingerprint for a log event.

    The fingerprint represents the identity of an event,
    not the exact timestamp of an individual log.
    """

    normalized_message = normalize_log_message(message)

    fingerprint_source = "|".join(
        [
            str(client_id),
            str(server_id),
            str(application_id),
            level.strip().upper(),
            normalized_message,
        ]
    )

    return hashlib.sha256(
        fingerprint_source.encode("utf-8")
    ).hexdigest()