from uuid import UUID

from sqlalchemy.orm import Session

from app.services.evidence_service import (
    create_evidence_from_group,
)

from app.services.investigation_pipeline import (
    start_investigation,
)


def process_correlation_group(
    db: Session,
    group,
):
    """
    Complete processing flow after a correlation group
    represents a real incident.

    Flow:

        CorrelationGroup
              ↓
        Evidence
              ↓
        ML
              ↓
        LLM
              ↓
        Investigation
              ↓
        Action Queue
    """

    # ==========================================================
    # 1. Create Evidence
    # ==========================================================

    evidence = create_evidence_from_group(
        db=db,
        group=group,
    )

    if evidence is None:
        return None

    # ==========================================================
    # 2. Get Incident ID
    # ==========================================================

    incident_id = evidence.incident_id

    if incident_id is None:
        return None

    # ==========================================================
    # 3. Run Investigation
    # ==========================================================

    investigation = start_investigation(
        db=db,
        incident_id=incident_id,
    )

    # ==========================================================
    # 4. Return Investigation
    # ==========================================================

    return investigation