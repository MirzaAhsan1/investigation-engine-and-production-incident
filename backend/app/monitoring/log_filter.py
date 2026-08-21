ERROR_LEVELS = {

    "ERROR",

    "CRITICAL",

    "FATAL",

}


ERROR_KEYWORDS = [

    "exception",

    "timeout",

    "queuepool",

    "connection refused",

    "connection reset",

    "http 500",

    "internal server error",

    "oom",

    "outofmemory",

    "segmentation fault",

    "panic",

    "database",

    "sqlalchemy",

    "failed",

    "crash",

    "unable to",

    "refused",

]


def is_interesting_log(level: str, message: str):

    level = level.upper()

    message = message.lower()

    # ------------------------
    # 0. Exclude INFO & DEBUG logs completely from DB storage
    # ------------------------

    if level in {"INFO", "DEBUG"}:

        return False, f"Filtered out non-critical level: {level}"

    # ------------------------
    # Level Check
    # ------------------------

    if level in ERROR_LEVELS:

        return True, f"Matched level: {level}"

    # ------------------------
    # Keyword Check
    # ------------------------

    for keyword in ERROR_KEYWORDS:

        if keyword in message:

            return True, f"Matched keyword: {keyword}"

    # ------------------------
    # Ignore
    # ------------------------

    return False, "Normal log"