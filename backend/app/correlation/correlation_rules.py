from datetime import timedelta

from app.models.log_event import LogEvent


# ============================================================
# Correlation Configuration
# ============================================================

CORRELATION_TIME_WINDOW_SECONDS = 60


# ============================================================
# Basic Identity Rules
# ============================================================

def same_client(
    current_log: LogEvent,
    previous_log: LogEvent,
) -> bool:

    return (
        current_log.client_id
        == previous_log.client_id
    )


def same_server(
    current_log: LogEvent,
    previous_log: LogEvent,
) -> bool:

    return (
        current_log.server_id
        == previous_log.server_id
    )


def same_application(
    current_log: LogEvent,
    previous_log: LogEvent,
) -> bool:

    return (
        current_log.application_id
        == previous_log.application_id
    )


# ============================================================
# Fingerprint Rule
# ============================================================

def same_fingerprint(
    current_log: LogEvent,
    previous_log: LogEvent,
) -> bool:

    if not current_log.fingerprint:
        return False

    if not previous_log.fingerprint:
        return False

    return (
        current_log.fingerprint
        == previous_log.fingerprint
    )


# ============================================================
# Time Window Rule
# ============================================================

def within_time_window(
    current_log: LogEvent,
    previous_log: LogEvent,
) -> bool:

    if not current_log.timestamp:
        return False

    if not previous_log.timestamp:
        return False

    difference = abs(
        current_log.timestamp
        - previous_log.timestamp
    )

    return (
        difference
        <= timedelta(
            seconds=CORRELATION_TIME_WINDOW_SECONDS
        )
    )


# ============================================================
# Message Similarity Rule
# ============================================================

def related_message(
    current_log: LogEvent,
    previous_log: LogEvent,
) -> bool:

    if not current_log.message:
        return False

    if not previous_log.message:
        return False

    current_message = (
        current_log.message
        .lower()
        .strip()
    )

    previous_message = (
        previous_log.message
        .lower()
        .strip()
    )

    # Exact message match
    if current_message == previous_message:
        return True

    # Basic keyword relationship
    keywords = [
        "timeout",
        "connection",
        "database",
        "database connection",
        "crash",
        "crashloopbackoff",
        "memory",
        "out of memory",
        "health check",
        "health check failed",
        "connection pool",
        "500",
        "internal server error",
    ]

    for keyword in keywords:

        if (
            keyword in current_message
            and keyword in previous_message
        ):
            return True

    return False


# ============================================================
# Main Correlation Rule
# ============================================================

def should_correlate(
    current_log: LogEvent,
    previous_log: LogEvent,
) -> tuple[bool, list[str]]:

    matched_rules = []


    # --------------------------------------------------------
    # Rule 1: Same Client
    # --------------------------------------------------------

    if same_client(
        current_log,
        previous_log,
    ):

        matched_rules.append(
            "SAME_CLIENT"
        )

    else:

        return False, []


    # --------------------------------------------------------
    # Rule 2: Same Server
    # --------------------------------------------------------

    if same_server(
        current_log,
        previous_log,
    ):

        matched_rules.append(
            "SAME_SERVER"
        )

    else:

        return False, []


    # --------------------------------------------------------
    # Rule 3: Same Application
    # --------------------------------------------------------

    if same_application(
        current_log,
        previous_log,
    ):

        matched_rules.append(
            "SAME_APPLICATION"
        )

    else:

        return False, []


    # --------------------------------------------------------
    # Rule 4: Time Window
    # --------------------------------------------------------

    if within_time_window(
        current_log,
        previous_log,
    ):

        matched_rules.append(
            "TIME_WINDOW"
        )

    else:

        return False, []


    # --------------------------------------------------------
    # Rule 5: Fingerprint
    # --------------------------------------------------------

    if same_fingerprint(
        current_log,
        previous_log,
    ):

        matched_rules.append(
            "SAME_FINGERPRINT"
        )

        return True, matched_rules


    # --------------------------------------------------------
    # Rule 6: Related Message
    # --------------------------------------------------------

    if related_message(
        current_log,
        previous_log,
    ):

        matched_rules.append(
            "RELATED_MESSAGE"
        )

        return True, matched_rules


    # --------------------------------------------------------
    # No Strong Correlation
    # --------------------------------------------------------

    return False, matched_rules