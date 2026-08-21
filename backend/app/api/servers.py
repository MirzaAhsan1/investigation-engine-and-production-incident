from fastapi import APIRouter
from fastapi import Depends

from sqlalchemy.orm import Session

from app.db.dependencies import get_db

from app.schemas.server import (
    ServerCreate,
    ServerResponse,
)

from app.services.server_service import (
    create_server,
    get_servers,
    get_servers_stats,
)

router = APIRouter(
    prefix="/servers",
    tags=["Servers"],
)


@router.post(
    "/",
    response_model=ServerResponse,
)
def create(
    payload: ServerCreate,
    db: Session = Depends(get_db),
):

    return create_server(
        db=db,
        payload=payload,
    )


@router.get(
    "/stats",
)
def list_servers_stats(
    db: Session = Depends(get_db),
):
    return get_servers_stats(
        db=db,
    )


@router.get(
    "/",
    response_model=list[ServerResponse],
)
def list_servers(
    db: Session = Depends(get_db),
):

    return get_servers(
        db=db,
    )