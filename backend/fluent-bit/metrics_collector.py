#!/usr/bin/env python3

import json
import subprocess
import time
from datetime import datetime, timezone

import requests


# ============================================================
# CONFIG
# ============================================================

CONTAINER_NAME = "fraud-dummy"

METRICS_API_URL = "http://localhost:8000/api/metrics/ingest"

API_KEY = "b4c7bfc5a797e94482a67da6564f97fb63797439e9d421227755c762b3cf80f5"

HOST = "fraud-server-01"

INTERVAL_SECONDS = 10


# ============================================================
# GET DOCKER STATS
# ============================================================

def get_container_stats():

    command = [
        "docker",
        "stats",
        CONTAINER_NAME,
        "--no-stream",
        "--format",
        "{{json .}}",
    ]

    result = subprocess.run(
        command,
        capture_output=True,
        text=True,
        check=True,
    )

    return json.loads(result.stdout.strip())


# ============================================================
# CONVERT PERCENTAGE
# ============================================================

def parse_percent(value):

    if not value:
        return None

    return float(value.replace("%", "").strip())


def get_disk_usage():

    command = [
        "docker",
        "exec",
        CONTAINER_NAME,
        "df",
        "-P",
        "/",
    ]

    result = subprocess.run(
        command,
        capture_output=True,
        text=True,
        check=True,
    )

    lines = result.stdout.strip().splitlines()

    if len(lines) < 2:
        return None

    # Example:
    # overlay  228G  46G  171G  21% /

    fields = lines[-1].split()

    if len(fields) < 5:
        return None

    return float(
        fields[4].replace("%", "")
    )

def get_disk_io_wait():

    command = [
        "iostat",
        "-c",
        "1",
        "2",
    ]

    result = subprocess.run(
        command,
        capture_output=True,
        text=True,
        check=True,
    )

    lines = result.stdout.splitlines()

    # Find all avg-cpu blocks
    avg_cpu_indexes = [
        i
        for i, line in enumerate(lines)
        if line.strip().startswith("avg-cpu:")
    ]

    if not avg_cpu_indexes:
        return None

    # Use the latest iostat sample
    index = avg_cpu_indexes[-1]

    # Values are immediately after avg-cpu header
    if index + 1 >= len(lines):
        return None

    values = lines[index + 1].split()

    # Expected:
    # %user %nice %system %iowait %steal %idle
    if len(values) < 6:
        return None

    try:
        # values[3] = %iowait
        return float(values[3])

    except (ValueError, TypeError):
        return None

# ============================================================
# BUILD METRIC PAYLOAD
# ============================================================

def build_metric(stats):

    return {
        "api_key": API_KEY,

        "host": HOST,

        "container_name": CONTAINER_NAME,

        "timestamp": datetime.now(timezone.utc).isoformat(),

        "cpu_usage": parse_percent(
            stats.get("CPUPerc")
        ),

        "memory_usage": parse_percent(
            stats.get("MemPerc")
        ),

        "disk_usage": get_disk_usage(),

        "disk_io_wait": get_disk_io_wait(),

        "api_latency": None,

        "http_5xx_count": None,

        "http_4xx_count": None,

        "request_per_second": None,

        "request_count": None,

        "deployment_changed": None,
    }

    


# ============================================================
# SEND TO INVESTIGATION API
# ============================================================

def send_metric(metric):

    response = requests.post(
        METRICS_API_URL,
        json=metric,
        timeout=10,
    )

    response.raise_for_status()

    return response.json()


# ============================================================
# MAIN LOOP
# ============================================================

def main():

    print(
        f"Starting container metrics collector for "
        f"{CONTAINER_NAME}",
        flush=True,
    )

    while True:

        try:

            stats = get_container_stats()

            metric = build_metric(stats)

            print(
                "Collected:",
                json.dumps(metric),
                flush=True,
            )

            result = send_metric(metric)

            print(
                "API response:",
                json.dumps(result),
                flush=True,
            )

        except Exception as exc:

            print(
                f"Metrics collection error: {exc}",
                flush=True,
            )

        time.sleep(INTERVAL_SECONDS)


if __name__ == "__main__":
    main()
