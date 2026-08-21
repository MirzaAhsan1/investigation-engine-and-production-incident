from datetime import timedelta


CORRELATION_TIME_WINDOW_SECONDS = 60


def should_correlate(
    existing_group,
    log,
):
    """
    Decide whether a log belongs
    to an existing correlation group.
    """

    # --------------------------------------------------------
    # Rule 1: Same client
    # --------------------------------------------------------

    if (
        existing_group.client_id
        != log.client_id
    ):
        return False


    # --------------------------------------------------------
    # Rule 2: Same server
    # --------------------------------------------------------

    if (
        existing_group.server_id
        != log.server_id
    ):
        return False


    # --------------------------------------------------------
    # Rule 3: Same application
    # --------------------------------------------------------

    if (
        existing_group.application_id
        != log.application_id
    ):
        return False


    # --------------------------------------------------------
    # Rule 4: Time window
    # --------------------------------------------------------

    if (
        log.timestamp
        - existing_group.last_seen
        > timedelta(
            seconds=CORRELATION_TIME_WINDOW_SECONDS
        )
    ):
        return False


    return True