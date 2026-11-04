import re
from collections import defaultdict
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.application import Application


# ============================================================
# INTERNAL CONTAINER FILTERING
# ------------------------------------------------------------
# Same idea as the fluent-bit Lua `is_internal` blacklist —
# kept here too so the applications registry and the log
# pipeline agree on what counts as a "real" client app vs.
# infra/DB/monitoring noise. If you update one list, update
# the other.
# ============================================================

_INTERNAL_PATTERNS = [
    r"^fluent-bit-",
    r"^coolify-log-drain",
    r"^coolify-sentinel",
    r"^coolify-proxy$",
    r"^coolify-db$",
    r"^coolify$",
    r"^traefik-metrics-poller-",
    r"^code-server-",
    r"^dozzle-",
    r"^jenkins-",
    r"^mysql-database-",
    r"^postgresql-database-",
    r"^postgresql-toka",
    r"^postgres-",
    r"^postgresql-",
    r"^redis-database-",
    r"^redis-",
    r"^mongodb-",
    r"^n8n-with-postgres",
    r"^neon-ws-proxy-",
    r"^phpmyadmin-",
    r"^service-",
    r"^supabase-",
    r"^docker-valkey-",
    r"^ecommerce_db$",
    r"^hotel-booking-db$",
]

_INTERNAL_RE = [re.compile(p) for p in _INTERNAL_PATTERNS]


def is_internal_container(name: str) -> bool:
    return any(pattern.match(name) for pattern in _INTERNAL_RE)


# ============================================================
# STABLE RESOURCE KEY
# ------------------------------------------------------------
# Coolify appends a per-deploy/per-instance suffix to the raw
# container name (e.g. "-072047524781", "-proxy", "-kafka-1").
# That suffix changes on every redeploy, so it can't be used as
# the identity of a "logical service" across redeploys. This
# strips it back down to the stable part so the same service
# is recognized across deploys instead of creating a new row
# each time.
# ============================================================

_TIMESTAMP_SUFFIX_RE = re.compile(r"-\d{9,15}$")
_NAMED_SUFFIX_RE = re.compile(r"-(proxy|kafka-\d+)$")


def stable_resource_key(container_name: str) -> str:
    key = _TIMESTAMP_SUFFIX_RE.sub("", container_name)
    key = _NAMED_SUFFIX_RE.sub("", key)
    return key


# ============================================================
# CRUD
# ============================================================

def create_application(
    db: Session,
    payload,
):
    # 1. Never register infra/DB/monitoring containers as
    #    client applications.
    if is_internal_container(payload.container_name):
        return None

    key = stable_resource_key(payload.container_name)

    # 2. Look for an existing active row for this same logical
    #    service on this server (matched on the stable key, not
    #    the raw container_name).
    candidates = (
        db.query(Application)
        .filter(
            Application.server_id == payload.server_id,
            Application.is_active == True,
        )
        .all()
    )
    existing = next(
        (
            app
            for app in candidates
            if stable_resource_key(app.container_name) == key
        ),
        None,
    )

    if existing:
        # Redeploy of an already-known service — update in place
        # instead of inserting a duplicate row.
        existing.container_name = payload.container_name
        existing.name = payload.name
        existing.provider = payload.provider
        if payload.resource_uuid:
            existing.resource_uuid = payload.resource_uuid
        db.commit()
        db.refresh(existing)
        return existing

    # 3. Genuinely new service — insert.
    application = Application(
        server_id=payload.server_id,
        name=payload.name,
        container_name=payload.container_name,
        provider=payload.provider,
        resource_uuid=payload.resource_uuid,
    )

    db.add(application)
    db.commit()
    db.refresh(application)

    return application


def get_applications(
    db: Session,
):
    return (
        db.query(Application)
        .filter(Application.is_active == True)
        .order_by(Application.created_at.asc())
        .all()
    )


def get_application(
    db: Session,
    application_id: UUID,
):
    return db.get(
        Application,
        application_id,
    )


def get_applications_by_server(
    db: Session,
    server_id: UUID,
):
    return (
        db.query(Application)
        .filter(
            Application.server_id == server_id,
            Application.is_active == True,
        )
        .all()
    )


def get_application_by_container(
    db: Session,
    server_id: UUID,
    container_name: str,
):
    return (
        db.query(Application)
        .filter(
            Application.server_id == server_id,
            Application.container_name == container_name,
            Application.is_active == True,
        )
        .first()
    )


# ============================================================
# ONE-TIME CLEANUP
# ------------------------------------------------------------
# Run this once (e.g. from a shell / management command) to
# collapse the duplicate rows that already exist from before
# this fix, and to deactivate rows for internal containers that
# got registered in the past.
#
#   from app.db.session import SessionLocal
#   from app.services.application_service import cleanup_duplicate_applications
#   db = SessionLocal()
#   cleanup_duplicate_applications(db)
#   db.close()
# ============================================================

def cleanup_duplicate_applications(db: Session):
    apps = (
        db.query(Application)
        .filter(Application.is_active == True)
        .order_by(Application.created_at.asc())
        .all()
    )

    groups = defaultdict(list)
    for app in apps:
        if is_internal_container(app.container_name):
            app.is_active = False
            continue
        key = (app.server_id, stable_resource_key(app.container_name))
        groups[key].append(app)

    for rows in groups.values():
        if len(rows) > 1:
            # Keep the most recently created row active, mark the
            # rest (the stale/old-deploy duplicates) inactive.
            for stale in rows[:-1]:
                stale.is_active = False

    db.commit()