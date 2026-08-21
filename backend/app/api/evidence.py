from uuid import UUID

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)
from sqlalchemy.orm import Session

from app.db.dependencies import get_db

from app.schemas.evidence import (
    EvidenceCreate,
    EvidenceResponse,
)

from app.services.evidence_service import (
    create_evidence,
    get_evidence_by_incident,
)

router = APIRouter(
    prefix="/evidence",
    tags=["Evidence"],
)


@router.post(
    "/",
    response_model=EvidenceResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_new_evidence(
    evidence: EvidenceCreate,
    db: Session = Depends(get_db),
):

    result = create_evidence(
        db=db,
        evidence_data=evidence,
    )

    if result is None:
        raise HTTPException(
            status_code=404,
            detail="Incident not found",
        )

    return result


@router.get(
    "/{incident_id}",
    response_model=EvidenceResponse,
)
def get_evidence(
    incident_id: UUID,
    db: Session = Depends(get_db),
):

    evidence = get_evidence_by_incident(
        db=db,
        incident_id=incident_id,
    )

    if evidence is None:
        raise HTTPException(
            status_code=404,
            detail="Evidence not found",
        )

    return evidence