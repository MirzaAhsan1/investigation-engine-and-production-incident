#!/usr/bin/env python3

import json
import sys
import time
from collections import deque
from datetime import datetime, timezone


WINDOW_SECONDS = 10

events = deque()


def process_event(event):
    now = time.time()

    status_code = int(event.get("status_code", 0))
    duration = float(event.get("duration", 0))

    events.append(
        {
            "timestamp": now,
            "status_code": status_code,
            "duration": duration,
        }
    )

    cutoff = now - WINDOW_SECONDS

    while events and events[0]["timestamp"] < cutoff:
        events.popleft()


def calculate_metrics():
    if not events:
        return {
            "api_latency": 0.0,
            "http_4xx_count": 0,
            "http_5xx_count": 0,
            "request_per_second": 0.0,
        }

    total_requests = len(events)

    total_latency = sum(
        event["duration"]
        for event in events
    )

    api_latency = (
        total_latency / total_requests
    )

    http_4xx_count = sum(
        1
        for event in events
        if 400 <= event["status_code"] < 500
    )

    http_5xx_count = sum(
        1
        for event in events
        if event["status_code"] >= 500
    )

    request_per_second = (
        total_requests / WINDOW_SECONDS
    )

    return {
        "api_latency": round(api_latency, 3),
        "http_4xx_count": http_4xx_count,
        "http_5xx_count": http_5xx_count,
        "request_per_second": round(
            request_per_second,
            3,
        ),
    }


def main():
    last_emit = time.time()

    for line in sys.stdin:

        line = line.strip()

        if not line:
            continue

        try:
            event = json.loads(line)

        except json.JSONDecodeError:
            continue

        process_event(event)

        now = time.time()

        if now - last_emit >= WINDOW_SECONDS:

            metrics = calculate_metrics()

            output = {
                "timestamp": datetime.now(
                    timezone.utc
                ).isoformat(),

                "api_latency": metrics[
                    "api_latency"
                ],

                "http_4xx_count": metrics[
                    "http_4xx_count"
                ],

                "http_5xx_count": metrics[
                    "http_5xx_count"
                ],

                "request_per_second": metrics[
                    "request_per_second"
                ],
            }

            print(
                json.dumps(output),
                flush=True,
            )

            last_emit = now


if __name__ == "__main__":
    main()