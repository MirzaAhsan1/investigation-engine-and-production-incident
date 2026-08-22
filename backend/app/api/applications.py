from fastapi import APIRouter
from fastapi import Depends

from sqlalchemy.orm import Session

from app.db.dependencies import get_db

from app.schemas.application import (
    ApplicationCreate,
    ApplicationResponse,
)

from app.services.application_service import (
    create_application,
    get_applications,
)

router = APIRouter(
    prefix="/applications",
    tags=["Applications"],
)


@router.post(
    "",
    response_model=ApplicationResponse,
)
def create(
    payload: ApplicationCreate,
    db: Session = Depends(get_db),
):

    return create_application(
        db=db,
        payload=payload,
    )


@router.get(
    "",
    response_model=list[ApplicationResponse],
)
def list_applications(
    db: Session = Depends(get_db),
):

    return get_applications(
        db=db,
    )