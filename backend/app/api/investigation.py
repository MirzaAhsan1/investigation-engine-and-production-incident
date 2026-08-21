from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.dependencies import get_db

from app.schemas.investigation import (
    InvestigationCreate,
    InvestigationResponse,
)

from app.services.investigation_pipeline import (
    start_investigation,
)

from app.services.investigation_pipeline import (
    get_investigation_by_incident,
    get_full_report,
)


router = APIRouter(
    prefix="/investigations",
    tags=["Investigations"],
)


# ============================================================
# START INVESTIGATION
# ============================================================

@router.post(
    "/",
    response_model=InvestigationResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_new_investigation(
    investigation: InvestigationCreate,
    db: Session = Depends(get_db),
):
    """
    Start an investigation for an existing incident.

    Flow:

        Incident
            ↓
        Evidence
            ↓
        Feature Extraction
            ↓
        Investigation
    """

    result = start_investigation(
        db=db,
        incident_id=investigation.incident_id,
    )

    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Incident not found",
        )

    return result


# ============================================================
# GET INVESTIGATION
# ============================================================

@router.get(
    "/{incident_id}",
    response_model=InvestigationResponse,
)
def get_investigation(
    incident_id: UUID,
    db: Session = Depends(get_db),
):
    """
    Get investigation for an incident.
    """

    investigation = get_investigation_by_incident(
        db=db,
        incident_id=incident_id,
    )

    if investigation is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Investigation not found",
        )

    return investigation


# ============================================================
# GET INVESTIGATION REPORT
# ============================================================

@router.get(
    "/report/{incident_id}",
)
def investigation_report(
    incident_id: UUID,
    db: Session = Depends(get_db),
):
    """
    Return the complete investigation report.

    Report contains the investigation result
    and collected evidence/findings.
    """

    report = get_full_report(
        db=db,
        incident_id=incident_id,
    )

    if report is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Investigation report not found",
        )

    return report