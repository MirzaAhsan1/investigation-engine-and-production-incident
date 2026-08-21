def classify_log_level(message: str) -> str:
    """
    Infer a log level from raw container stdout/stderr text
    when the log line has no explicit level field.
    """

    m = message.upper()

    if "CRITICAL" in m or "FATAL" in m:
        return "CRITICAL"

    if "ERROR" in m or "EXCEPTION" in m or "TRACEBACK" in m:
        return "ERROR"

    if "WARN" in m:
        return "WARNING"

    if "DEBUG" in m:
        return "DEBUG"

    return "INFO"