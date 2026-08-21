from pathlib import Path

import numpy as np
import pandas as pd


# ============================================================
# CONFIG
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[1]

OUTPUT_FILE = (
    BASE_DIR
    / "datasets"
    / "production_incidents_v6.csv"
)

N_SAMPLES = 30000

RANDOM_STATE = 42

rng = np.random.default_rng(
    RANDOM_STATE
)


# ============================================================
# HELPERS
# ============================================================

def clip(
    values,
    minimum,
    maximum,
):
    return np.clip(
        values,
        minimum,
        maximum,
    )


# ============================================================
# GENERATE DATA
# ============================================================

def generate_dataset():

    n = N_SAMPLES

    # ========================================================
    # BASE METRICS
    # ========================================================

    cpu_usage = clip(
        rng.normal(45, 15, n),
        1,
        100,
    )

    memory_usage = clip(
        rng.normal(50, 15, n),
        1,
        100,
    )

    disk_usage = clip(
        rng.normal(50, 15, n),
        1,
        100,
    )

    disk_io_wait = clip(
        rng.exponential(1.5, n),
        0,
        30,
    )

    api_latency = clip(
        rng.lognormal(
            np.log(120),
            0.5,
            n,
        ),
        5,
        5000,
    )

    http_5xx_count = rng.poisson(
        2,
        n,
    )

    http_4xx_count = rng.poisson(
        8,
        n,
    )

    request_per_second = clip(
        rng.gamma(
            4,
            10,
            n,
        ),
        0.1,
        500,
    )

    error_rate = clip(
        rng.beta(
            1.5,
            20,
            n,
        ),
        0,
        1,
    )

    db_connections = rng.integers(
        5,
        100,
        n,
    )

    failed_login_attempts = rng.poisson(
        1.5,
        n,
    )

    packet_loss = clip(
        rng.exponential(
            0.5,
            n,
        ),
        0,
        20,
    )

    network_latency = clip(
        rng.lognormal(
            np.log(40),
            0.5,
            n,
        ),
        1,
        2000,
    )

    restart_count = rng.poisson(
        0.4,
        n,
    )

    active_containers = rng.integers(
        3,
        15,
        n,
    )

    ssl_certificate_days_left = clip(
        rng.normal(
            100,
            40,
            n,
        ),
        0,
        365,
    )

    # ========================================================
    # INCIDENT CATEGORY
    #
    # Explicitly create classes.
    # ========================================================

    categories = rng.choice(
        [
            "NORMAL",
            "DATABASE",
            "SECURITY",
            "DEPLOYMENT",
            "INFRASTRUCTURE",
        ],
        size=n,
        p=[
            0.45,
            0.20,
            0.15,
            0.10,
            0.10,
        ],
    )

    incident_category = categories.copy()

    # ========================================================
    # DEPLOYMENT INCIDENTS
    # ========================================================

    deployment_mask = (
        categories == "DEPLOYMENT"
    )

    deployment_changed = np.zeros(
        n,
        dtype=int,
    )

    deployment_changed[
        deployment_mask
    ] = 1

    restart_count[
        deployment_mask
    ] = rng.integers(
        2,
        8,
        deployment_mask.sum(),
    )

    active_containers[
        deployment_mask
    ] = rng.integers(
        1,
        5,
        deployment_mask.sum(),
    )

    api_latency[
        deployment_mask
    ] *= rng.uniform(
        1.5,
        3.0,
        deployment_mask.sum(),
    )

    http_5xx_count[
        deployment_mask
    ] += rng.integers(
        5,
        25,
        deployment_mask.sum(),
    )

    error_rate[
        deployment_mask
    ] = rng.uniform(
        0.08,
        0.30,
        deployment_mask.sum(),
    )

    # ========================================================
    # INFRASTRUCTURE INCIDENTS
    # ========================================================

    infrastructure_mask = (
        categories == "INFRASTRUCTURE"
    )

    infrastructure_types = rng.choice(
        [
            "CPU",
            "MEMORY",
            "DISK",
            "IO",
        ],
        size=infrastructure_mask.sum(),
    )

    infrastructure_indexes = np.where(
        infrastructure_mask
    )[0]

    for index, incident_type in zip(
        infrastructure_indexes,
        infrastructure_types,
    ):

        if incident_type == "CPU":

            cpu_usage[index] = rng.uniform(
                88,
                100,
            )

        elif incident_type == "MEMORY":

            memory_usage[index] = rng.uniform(
                88,
                100,
            )

        elif incident_type == "DISK":

            disk_usage[index] = rng.uniform(
                88,
                100,
            )

        elif incident_type == "IO":

            disk_io_wait[index] = rng.uniform(
                10,
                30,
            )

    # ========================================================
    # DATABASE INCIDENTS
    # ========================================================

    database_mask = (
        categories == "DATABASE"
    )

    database_types = rng.choice(
        [
            "CONNECTIONS",
            "ERROR_RATE",
        ],
        size=database_mask.sum(),
    )

    database_indexes = np.where(
        database_mask
    )[0]

    for index, incident_type in zip(
        database_indexes,
        database_types,
    ):

        if incident_type == "CONNECTIONS":

            db_connections[index] = rng.integers(
                90,
                150,
            )

        else:

            error_rate[index] = rng.uniform(
                0.20,
                0.60,
            )

    # ========================================================
    # SECURITY INCIDENTS
    # ========================================================

    security_mask = (
        categories == "SECURITY"
    )

    security_types = rng.choice(
        [
            "LOGIN",
            "NETWORK",
            "SSL",
        ],
        size=security_mask.sum(),
    )

    security_indexes = np.where(
        security_mask
    )[0]

    for index, incident_type in zip(
        security_indexes,
        security_types,
    ):

        if incident_type == "LOGIN":

            failed_login_attempts[index] = rng.integers(
                10,
                50,
            )

        elif incident_type == "NETWORK":

            packet_loss[index] = rng.uniform(
                5,
                20,
            )

            network_latency[index] = rng.uniform(
                500,
                2000,
            )

        else:

            ssl_certificate_days_left[index] = rng.uniform(
                0,
                10,
            )

    # ========================================================
    # CAUSE
    # ========================================================

    incident_cause = np.full(
        n,
        "NO_INCIDENT",
        dtype=object,
    )

    # --------------------------------------------------------
    # Deployment
    # --------------------------------------------------------

    incident_cause[
        deployment_mask
    ] = "RECENT_DEPLOYMENT"

    # --------------------------------------------------------
    # Infrastructure
    # --------------------------------------------------------

    infrastructure_indexes = np.where(
        infrastructure_mask
    )[0]

    for index, incident_type in zip(
        infrastructure_indexes,
        infrastructure_types,
    ):

        if incident_type == "CPU":

            incident_cause[index] = (
                "HIGH_CPU_USAGE"
            )

        elif incident_type == "MEMORY":

            incident_cause[index] = (
                "HIGH_MEMORY_USAGE"
            )

        elif incident_type == "DISK":

            incident_cause[index] = (
                "HIGH_DISK_USAGE"
            )

        elif incident_type == "IO":

            incident_cause[index] = (
                "HIGH_DISK_IO_WAIT"
            )

    # --------------------------------------------------------
    # Database
    # --------------------------------------------------------

    database_indexes = np.where(
        database_mask
    )[0]

    for index, incident_type in zip(
        database_indexes,
        database_types,
    ):

        if incident_type == "CONNECTIONS":

            incident_cause[index] = (
                "DATABASE_CONNECTION_EXHAUSTION"
            )

        else:

            incident_cause[index] = (
                "HIGH_DATABASE_ERROR_RATE"
            )

    # --------------------------------------------------------
    # Security
    # --------------------------------------------------------

    security_indexes = np.where(
        security_mask
    )[0]

    for index, incident_type in zip(
        security_indexes,
        security_types,
    ):

        if incident_type == "LOGIN":

            incident_cause[index] = (
                "BRUTE_FORCE_LOGIN_ATTEMPTS"
            )

        elif incident_type == "NETWORK":

            incident_cause[index] = (
                "HIGH_NETWORK_LATENCY"
            )

        else:

            incident_cause[index] = (
                "SSL_CERTIFICATE_EXPIRING"
            )

    # ========================================================
    # DATAFRAME
    # ========================================================

    df = pd.DataFrame(
        {

            "cpu_usage": cpu_usage,

            "memory_usage": memory_usage,

            "disk_usage": disk_usage,

            "disk_io_wait": disk_io_wait,

            "api_latency": api_latency,

            "http_5xx_count": http_5xx_count,

            "http_4xx_count": http_4xx_count,

            "request_per_second": request_per_second,

            "error_rate": error_rate,

            "db_connections": db_connections,

            "failed_login_attempts": (
                failed_login_attempts
            ),

            "packet_loss": packet_loss,

            "network_latency": network_latency,

            "restart_count": restart_count,

            "active_containers": active_containers,

            "deployment_changed": (
                deployment_changed
            ),

            "ssl_certificate_days_left": (
                ssl_certificate_days_left
            ),

            "incident_category": (
                incident_category
            ),

            "incident_cause": (
                incident_cause
            ),
        }
    )

    return df


# ============================================================
# MAIN
# ============================================================

def main():

    print()
    print("=" * 70)
    print("GENERATING PRODUCTION INCIDENT DATASET V6")
    print("=" * 70)

    df = generate_dataset()

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    df.to_csv(
        OUTPUT_FILE,
        index=False,
    )

    print()
    print(
        f"Saved: {OUTPUT_FILE}"
    )

    print(
        f"Shape: {df.shape}"
    )

    print()
    print("=" * 70)
    print("CATEGORY DISTRIBUTION")
    print("=" * 70)

    print(
        df[
            "incident_category"
        ].value_counts()
    )

    print()
    print("=" * 70)
    print("CAUSE DISTRIBUTION")
    print("=" * 70)

    print(
        df[
            "incident_cause"
        ].value_counts()
    )


if __name__ == "__main__":
    main()