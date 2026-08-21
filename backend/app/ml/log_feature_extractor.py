LOG_FEATURE_COLUMNS = [

    "has_http_500",

    "has_http_502",

    "has_http_503",

    "has_http_504",

    "has_database_timeout",

    "has_connection_pool_exhausted",

    "has_deadlock",

    "has_null_pointer",

    "has_out_of_memory",

    "has_thread_starvation",

    "has_packet_loss",

    "has_dns_failure",

    "has_network_timeout",

    "has_sql_injection",

    "has_failed_login",

    "has_jwt_failure",

]


KEYWORDS = {

    "has_http_500": [
        "http 500",
        "internal server error",
    ],

    "has_http_502": [
        "http 502",
        "bad gateway",
    ],

    "has_http_503": [
        "http 503",
        "service unavailable",
    ],

    "has_http_504": [
        "http 504",
        "gateway timeout",
    ],

    "has_database_timeout": [
        "database connection timeout",
        "database timeout",
    ],

    "has_connection_pool_exhausted": [
        "connection pool exhausted",
        "too many connections",
    ],

    "has_deadlock": [
        "deadlock detected",
    ],

    "has_null_pointer": [
        "nullpointerexception",
        "null pointer",
    ],

    "has_out_of_memory": [
        "outofmemory",
        "out of memory",
        "memory leak",
    ],

    "has_thread_starvation": [
        "thread starvation",
    ],

    "has_packet_loss": [
        "packet loss",
    ],

    "has_dns_failure": [
        "dns resolution failed",
    ],

    "has_network_timeout": [
        "network timeout",
    ],

    "has_sql_injection": [
        "sql injection",
    ],

    "has_failed_login": [
        "failed login",
        "multiple failed login",
    ],

    "has_jwt_failure": [
        "jwt validation failed",
        "jwt expired",
    ],

}


def extract_log_features(
    logs: str | None,
) -> list[int]:

    if not logs:

        return [

            0

            for _ in LOG_FEATURE_COLUMNS

        ]

    logs = logs.lower()

    features = []

    for feature in LOG_FEATURE_COLUMNS:

        found = 0

        for keyword in KEYWORDS[feature]:

            if keyword in logs:

                found = 1

                break

        features.append(found)

    return features