from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.dependencies import (
    get_current_user,
    get_db,
)

from app.models.user import User
from app.models.incident import Incident

from app.schemas.incident import (
    IncidentCreate,
    IncidentResponse,
    IncidentDetailResponse,
)

from app.services.incident_service import (
    create_incident,
    get_all_incidents,
    get_incident_detail,
)


router = APIRouter(
    prefix="/incidents",
    tags=["Incidents"],
)


# ============================================================
# Create Manual Incident
# ============================================================

@router.post(
    "/",
    response_model=IncidentResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_incident_endpoint(
    incident: IncidentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_user
    ),
):
    """
    Manually create an incident.
    """

    return create_incident(
        db=db,
        incident_data=incident,
        current_user=current_user,
    )


# ============================================================
# Get All Incidents
# ============================================================

@router.get(
    "/",
    response_model=list[IncidentResponse],
)
def get_incidents_endpoint(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_user
    ),
):
    """
    Get all incidents.
    """

    return get_all_incidents(db=db)


# ============================================================
# Get Complete Incident Detail
# ============================================================

@router.get(
    "/{incident_id}/detail",
    response_model=IncidentDetailResponse,
)
def get_incident_detail_endpoint(
    incident_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_user
    ),
):
    """
    Get complete incident information.

    Response contains:

        Incident
            +
        Application / Container
            +
        Correlation Group
            +
        Evidence
    """

    detail = get_incident_detail(
        db=db,
        incident_id=incident_id,
    )

    if detail is None:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Incident not found",
        )

    return detail


# ============================================================
# Get Basic Incident By ID
# ============================================================

@router.get(
    "/{incident_id}",
    response_model=IncidentResponse,
)
def get_incident_by_id_endpoint(
    incident_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_user
    ),
):
    """
    Get basic incident information.
    """

    incident = db.get(
        Incident,
        incident_id,
    )

    if incident is None:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Incident not found",
        )

    return incident