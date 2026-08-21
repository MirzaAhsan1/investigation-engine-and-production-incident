from fastapi import APIRouter, Depends

from sqlalchemy.orm import Session

from app.db.dependencies import get_db

from app.services.monitoring_worker import (
    process_pending_logs,
)


router = APIRouter(
    prefix="/monitoring",
    tags=["Monitoring"],
)


@router.post("/process")
def process_logs(
    db: Session = Depends(get_db),
):

    return process_pending_logs(
        db=db,
    )