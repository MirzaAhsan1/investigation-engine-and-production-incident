from uuid import UUID

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)

from sqlalchemy.orm import Session

from app.db.dependencies import get_db

from app.schemas.incident_evidence import (
    IncidentEvidencePackage,
)

from app.services.incident_evidence_service import (
    build_incident_evidence_package,
)


router = APIRouter(
    prefix="/incidents",
    tags=["Incident Evidence"],
)


# ==========================================================
# Get Incident Evidence
# ==========================================================

@router.get(
    "/{incident_id}/evidence",
    response_model=IncidentEvidencePackage,
    status_code=status.HTTP_200_OK,
)
def get_incident_evidence(
    incident_id: UUID,
    db: Session = Depends(get_db),
):
    """
    Get complete evidence package for an incident.

    Evidence includes:

    - Incident information
    - Correlation group
    - Application/system metrics
    - Metric summary
    - Evidence time window
    """

    evidence_package = (
        build_incident_evidence_package(
            db=db,
            incident_id=incident_id,
        )
    )

    # ======================================================
    # Incident Not Found
    # ======================================================

    if evidence_package is None:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "status": "incident_not_found",
                "reason": (
                    f"Incident "
                    f"'{incident_id}' "
                    "does not exist"
                ),
            },
        )

    # ======================================================
    # Return Evidence
    # ======================================================

    return evidence_package