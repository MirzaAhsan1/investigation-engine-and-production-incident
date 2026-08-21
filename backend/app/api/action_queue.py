from uuid import UUID

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)

from sqlalchemy.orm import Session

from app.db.dependencies import get_db
from app.enums.action_status import ActionStatusEnum

from app.schemas.action_queue import (
    ActionResponse,
    ApproveActionRequest,
    RejectActionRequest,
)

from app.services.action_queue_service import (
    get_action,
    update_action_status,
    get_actions_by_investigation,
    get_actions_by_incident,
)


router = APIRouter(
    prefix="/actions",
    tags=["Action Queue"],
)


@router.get(
    "/investigation/{investigation_id}",
    response_model=list[ActionResponse],
)
def get_actions(
    investigation_id: UUID,
    db: Session = Depends(get_db),
):

    return get_actions_by_investigation(
        db,
        investigation_id,
    )


@router.get(
    "/incident/{incident_id}",
    response_model=list[ActionResponse],
)
def get_actions_by_incident_endpoint(
    incident_id: UUID,
    db: Session = Depends(get_db),
):
    return get_actions_by_incident(
        db,
        incident_id,
    )


@router.post(
    "/{action_id}/approve",
    response_model=ActionResponse,
)
@router.patch(
    "/{action_id}/approve",
    response_model=ActionResponse,
)
def approve(
    action_id: UUID,
    payload: ApproveActionRequest | None = None,
    db: Session = Depends(get_db),
):
    action = get_action(db, action_id)
    if action is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Action not found",
        )

    approved_by = payload.approved_by if payload else None
    return update_action_status(
        db=db,
        action=action,
        new_status=ActionStatusEnum.APPROVED,
        approved_by=approved_by,
    )


@router.post(
    "/{action_id}/reject",
    response_model=ActionResponse,
)
@router.post(
    "/{action_id}/deny",
    response_model=ActionResponse,
)
@router.patch(
    "/{action_id}/reject",
    response_model=ActionResponse,
)
@router.patch(
    "/{action_id}/deny",
    response_model=ActionResponse,
)
def reject(
    action_id: UUID,
    payload: RejectActionRequest | None = None,
    db: Session = Depends(get_db),
):
    action = get_action(db, action_id)
    if action is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Action not found",
        )

    approved_by = payload.approved_by if payload else None
    return update_action_status(
        db=db,
        action=action,
        new_status=ActionStatusEnum.REJECTED,
        approved_by=approved_by,
    )