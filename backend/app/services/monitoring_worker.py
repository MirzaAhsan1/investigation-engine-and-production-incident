from sqlalchemy.orm import Session

from app.models.log_event import LogEvent
from app.enums.log_status import LogStatusEnum

from app.services.monitoring_service import process_log_evidence
from app.services.investigation_pipeline import start_investigation


def process_pending_logs(
    db: Session,
):
    """
    Process all pending monitoring logs.

    Flow (per log, cheap — no ML/LLM):

        PENDING
           ↓
        PROCESSING
           ↓
        process_log_evidence()
           ↓
        Evidence + Incident (create/reuse)
           ↓
        COMPLETED

    Flow (once per unique incident touched in this batch,
    AFTER all logs above are processed):

        start_investigation()
           ↓
        ML Prediction + LLM Investigation
           ↓
        Investigation Record (create/update) + Action Queue

    This batching avoids running ML/LLM once per log — if
    several correlated logs in this batch belong to the same
    incident, the AI investigation still only runs once for
    that incident, using the latest combined evidence.

    If any step fails for a log:

        PROCESSING
           ↓
        FAILED
    """

    logs = (
        db.query(LogEvent)
        .filter(
            LogEvent.status == LogStatusEnum.PENDING
        )
        .order_by(
            LogEvent.created_at
        )
        .all()
    )

    processed = 0
    failed = 0

    touched_incident_ids = set()

    # ==============================================================
    # Phase 1: Correlate evidence + incident for every pending log
    # (no ML/LLM here)
    # ==============================================================

    for log in logs:

        try:

            # ==================================================
            # 1. Mark log as PROCESSING
            # ==================================================

            log.status = LogStatusEnum.PROCESSING

            db.commit()

            # ==================================================
            # 2. Correlate evidence + incident (no ML/LLM)
            # ==================================================

            incident_id = process_log_evidence(
                db=db,
                log=log,
            )

            if incident_id is not None:
                touched_incident_ids.add(incident_id)

            # ==================================================
            # 3. Mark as COMPLETED
            # ==================================================

            log.status = LogStatusEnum.COMPLETED

            db.commit()

            processed += 1

        except Exception as exc:

            # ==================================================
            # 4. Rollback failed transaction
            # ==================================================

            db.rollback()

            print(
                "[MONITORING WORKER] "
                f"Failed to process log {log.id}: {exc}"
            )

            # ==================================================
            # 5. Mark log as FAILED
            # ==================================================

            try:

                log.status = LogStatusEnum.FAILED

                db.commit()

            except Exception:

                db.rollback()

            failed += 1

    # ==============================================================
    # Phase 2: Run ML + LLM investigation ONCE per unique incident
    # touched in this batch.
    # ==============================================================

    investigated = 0
    investigation_failed = 0

    for incident_id in touched_incident_ids:

        try:

            start_investigation(
                db=db,
                incident_id=incident_id,
            )

            investigated += 1

        except Exception as exc:

            db.rollback()

            print(
                "[MONITORING WORKER] "
                f"Investigation failed for incident {incident_id}: {exc}"
            )

            investigation_failed += 1

    return {
        "processed": processed,
        "failed": failed,
        "investigated": investigated,
        "investigation_failed": investigation_failed,
    }