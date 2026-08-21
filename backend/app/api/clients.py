from fastapi import APIRouter
from fastapi import Depends

from sqlalchemy.orm import Session

from app.db.dependencies import get_db

from app.schemas.client import (
    ClientCreate,
    ClientResponse,
)

from app.services.client_service import (
    create_client,
    get_clients,
)

router = APIRouter(
    prefix="/clients",
    tags=["Clients"],
)


@router.post(
    "/",
    response_model=ClientResponse,
)
def create(
    payload: ClientCreate,
    db: Session = Depends(get_db),
):

    return create_client(
        db=db,
        payload=payload,
    )


@router.get(
    "/",
    response_model=list[ClientResponse],
)
def list_clients(
    db: Session = Depends(get_db),
):

    return get_clients(
        db=db,
    )