from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session, joinedload

from app.db.dependencies import get_db, get_current_user
from app.models.user import User
from app.models.log_event import LogEvent
from app.models.application import Application

from app.schemas.log_ingest import LogIngestRequest
from app.schemas.log_event import LogEventListItem

from app.services.log_ingestion_service import ingest_log_batch


router = APIRouter(
    prefix="/logs",
    tags=["Logs"],
)


# ==========================================================
# GET /api/logs — Read stored log events
# ==========================================================

@router.get(
    "",
    response_model=list[LogEventListItem],
)
def get_log_events(
    search: Optional[str] = Query(
        None,
        description="Search in log message",
    ),
    level: Optional[str] = Query(
        None,
        description="Filter by log level (ERROR, WARN, INFO, etc.)",
    ),
    status: Optional[str] = Query(
        None,
        description="Filter by processing status (PENDING, COMPLETED, FAILED, etc.)",
    ),
    container_name: Optional[str] = Query(
        None,
        description="Filter by application container name",
    ),
    correlation_group_id: Optional[UUID] = Query(
        None,
        description="Filter by correlation group ID",
    ),
    limit: int = Query(
        200,
        ge=1,
        le=1000,
        description="Max number of log events to return",
    ),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Return stored log events from the log_events table,
    ordered by timestamp descending (newest first).
    """

    query = (
        db.query(LogEvent)
        .options(
            joinedload(LogEvent.application),
            joinedload(LogEvent.server),
        )
    )

    if correlation_group_id:
        query = query.filter(
            LogEvent.correlation_group_id == correlation_group_id
        )

    if search:
        query = query.filter(
            LogEvent.message.ilike(f"%{search}%")
        )

    if level:
        query = query.filter(
            LogEvent.level == level.upper()
        )

    if status:
        query = query.filter(
            LogEvent.status == status.upper()
        )

    if container_name:
        query = query.join(LogEvent.application).filter(
            Application.container_name == container_name
        )

    log_events = (
        query
        .order_by(LogEvent.timestamp.desc())
        .limit(limit)
        .all()
    )

    results = []

    for log in log_events:
        results.append(
            LogEventListItem(
                id=log.id,
                level=log.level,
                message=log.message,
                timestamp=log.timestamp,
                status=log.status,
                occurrence_count=log.occurrence_count,
                first_seen=log.first_seen,
                last_seen=log.last_seen,
                fingerprint=log.fingerprint,
                correlation_group_id=log.correlation_group_id,
                container_name=(
                    log.application.container_name
                    if log.application
                    else None
                ),
                host=(
                    log.server.host
                    if log.server
                    else None
                ),
                application_name=(
                    log.application.name
                    if log.application
                    else None
                ),
                server_name=(
                    log.server.name
                    if log.server
                    else None
                ),
                created_at=log.created_at,
                updated_at=log.updated_at,
            )
        )

    return results


# ==========================================================
# POST /api/logs/ingest — Ingest a single log
# ==========================================================

@router.post("/ingest")
def ingest_single_log(
    log: LogIngestRequest,
    db: Session = Depends(get_db),
):
    results = ingest_log_batch(db=db, logs=[log])
    return results[0] if results else {"status": "error"}


# ==========================================================
# POST /api/logs/ingest/batch — Ingest batch logs
# ==========================================================

@router.post("/ingest/batch")
def ingest_batch_logs(
    logs: list[LogIngestRequest],
    db: Session = Depends(get_db),
):
    # Single batch call that avoids connection leaks
    results = ingest_log_batch(db=db, logs=logs)

    interesting = sum(
        1 for r in results if r.get("status") == "interesting"
    )
    ignored = sum(
        1 for r in results if r.get("status") == "ignored"
    )
    unauthorized = sum(
        1 for r in results if r.get("status") == "unauthorized"
    )
    duplicate = sum(
        1 for r in results if r.get("status") == "duplicate"
    )

    return {
        "received": len(logs),
        "interesting": interesting,
        "ignored": ignored,
        "duplicate": duplicate,
        "unauthorized": unauthorized,
    }