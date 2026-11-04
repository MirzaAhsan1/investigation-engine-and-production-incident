from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models.application import Application
from app.models.system_metric import SystemMetric

from app.integrations.coolify_client import CoolifyClient


# ============================================================
# Status String Parsing
# ============================================================
#
# Coolify returns status as "<state>:<health>", e.g.:
#     "running:healthy"
#     "running:unhealthy"
#     "exited:unhealthy"
#     "restarting:unhealthy"
#
# We only derive active_containers from this (1 running app
# container, 0 if it's not up). restart_count is intentionally
# OUT of scope for now (Coolify doesn't expose a raw counter;
# revisit if/when we want to track state transitions).
# ============================================================

RUNNING_STATES = ("running",)


def _parse_running(status: str | None) -> int | None:

    if not status:
        return None

    state = status.split(":")[0].strip().lower()

    return 1 if state in RUNNING_STATES else 0


def _parse_deployment_timestamp(deployment: dict | None):

    if not deployment:
        return None

    raw = (
        deployment.get("created_at")
        or deployment.get("updated_at")
    )

    if not raw:
        return None

    try:

        # Coolify timestamps are typically ISO-8601 UTC.
        return datetime.fromisoformat(
            raw.replace("Z", "+00:00")
        )

    except (ValueError, AttributeError):

        return None


# ============================================================
# Get Coolify Applications Eligible For Polling
# ============================================================

def get_coolify_applications(
    db: Session,
):
    """
    Active applications registered against the Coolify
    provider that have a resource_uuid we can poll.
    """

    return (
        db.query(Application)
        .filter(
            Application.is_active == True,
            Application.provider == "coolify",
            Application.resource_uuid.isnot(None),
        )
        .all()
    )


# ============================================================
# Poll One Application
# ============================================================

def poll_application(
    db: Session,
    application: Application,
    client: CoolifyClient,
):
    """
    Fetch current status + latest deployment for a single
    application and write a SystemMetric row reflecting them.

    Returns the created SystemMetric, or None if the Coolify
    call failed (network/API error) — failures here must never
    take down the whole polling cycle for other applications.
    """

    try:

        status = client.get_application_status(
            application.resource_uuid,
        )

        latest_deployment = client.get_latest_deployment(
            application.resource_uuid,
        )

    except Exception as exc:

        print(
            "[COOLIFY STATUS] "
            f"Failed to poll application "
            f"{application.id} "
            f"({application.name}): {exc}"
        )

        return None

    # --------------------------------------------------------
    # active_containers
    # --------------------------------------------------------

    active_containers = _parse_running(status)

    # --------------------------------------------------------
    # deployment_changed
    #
    # Compare the latest deployment's timestamp against the
    # last one we already recorded for this application.
    # --------------------------------------------------------

    deployment_timestamp = _parse_deployment_timestamp(
        latest_deployment
    )

    deployment_changed = False

    if deployment_timestamp is not None:

        previous = application.last_known_deployment_at

        if previous is None:

            # First time we've ever seen a deployment
            # timestamp for this application — establish
            # baseline, don't flag it as "changed".
            deployment_changed = False

        else:

            previous_utc = (
                previous
                if previous.tzinfo is not None
                else previous.replace(tzinfo=timezone.utc)
            )

            deployment_changed = (
                deployment_timestamp > previous_utc
            )

        if (
            deployment_changed
            or application.last_known_deployment_at is None
        ):

            application.last_known_deployment_at = (
                deployment_timestamp
            )

    # --------------------------------------------------------
    # Write SystemMetric row
    #
    # This is a Coolify-derived, application-scoped row —
    # CPU/Memory/Disk stay NULL here since those come from the
    # separate Fluent Bit server-wide ingestion path.
    # --------------------------------------------------------

    metric = SystemMetric(
        client_id=application.server.client_id,
        server_id=application.server_id,
        application_id=application.id,
        timestamp=datetime.now(timezone.utc),
        active_containers=active_containers,
        deployment_changed=deployment_changed,
    )

    db.add(metric)

    return metric


# ============================================================
# Poll All Applications
# ============================================================

def poll_all_applications(
    db: Session,
):
    """
    Poll Coolify for every eligible application and persist
    the results as SystemMetric rows.

    Called on its own periodic loop (see monitoring_scheduler),
    separate from the Fluent Bit log/metric ingestion path.
    """

    applications = get_coolify_applications(
        db=db,
    )

    if not applications:

        return {
            "polled": 0,
            "failed": 0,
        }

    client = CoolifyClient()

    polled = 0
    failed = 0

    for application in applications:

        metric = poll_application(
            db=db,
            application=application,
            client=client,
        )

        if metric is not None:

            polled += 1

        else:

            failed += 1

    try:

        db.commit()

    except Exception as exc:

        db.rollback()

        print(
            "[COOLIFY STATUS] "
            f"Commit failed: {exc}"
        )

        return {
            "polled": 0,
            "failed": len(applications),
        }

    return {
        "polled": polled,
        "failed": failed,
    }
