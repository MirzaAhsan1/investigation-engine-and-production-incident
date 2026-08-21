from sqlalchemy.orm import Session

from app.models.log_event import LogEvent

from app.services.evidence_aggregation_service import (
    create_or_update_evidence_from_group,
)

from app.services.incident_service import (
    create_incident_from_group,
)


def process_log_evidence(
    db: Session,
    log: LogEvent,
):
    """
    Correlate a log's Evidence and ensure it is linked to an
    Incident.

    Flow:

        LogEvent
            ↓
        CorrelationGroup (already set during ingestion)
            ↓
        Evidence (create/update)
            ↓
        Incident (create or reuse)

    IMPORTANT:

    This does NOT trigger ML / LLM investigation. Running the
    AI investigation here would mean it runs once per LOG,
    which is wasteful and costly when many logs in the same
    worker cycle belong to the same incident (e.g. a burst of
    5 correlated errors would trigger 5 separate LLM calls
    for what is really one ongoing incident).

    Instead, the caller (monitoring_worker.process_pending_logs)
    collects the set of incident IDs touched across the whole
    batch and triggers investigation_pipeline.start_investigation()
    exactly ONCE per unique incident, after all logs in the
    batch have been correlated and their evidence updated.

    Returns:

        The incident.id this log's evidence was attached to,
        or None if the log had no correlation group.
    """

    # ==========================================================
    # 1. Get Correlation Group
    # ==========================================================

    group = log.correlation_group

    if not group:
        raise ValueError(
            f"Log {log.id} has no correlation group associated."
        )

    # ==========================================================
    # 2. Create / Update Evidence
    #
    # Evidence is created BEFORE Incident because
    # create_incident_from_group() requires Evidence.
    # ==========================================================

    evidence = create_or_update_evidence_from_group(
        db=db,
        group=group,
    )

    if evidence is None:
        raise ValueError(
            "Failed to create evidence from correlation group"
        )

    # ==========================================================
    # 3. Create / Reuse Incident
    # ==========================================================

    incident = create_incident_from_group(
        db=db,
        group=group,
        evidence=evidence,
    )

    if incident is None:
        raise ValueError(
            "Failed to create incident"
        )

    # ==========================================================
    # 4. Evidence should now be linked to Incident
    # ==========================================================

    if evidence.incident_id != incident.id:

        evidence.incident_id = incident.id

        db.flush()

    # ==========================================================
    # 5. Save
    # ==========================================================

    try:

        db.commit()

        db.refresh(incident)
        db.refresh(evidence)

    except Exception:

        db.rollback()

        raise

    # ==========================================================
    # 6. Return the incident this log contributed to
    # ==========================================================

    return incident.id