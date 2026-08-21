from datetime import datetime
from uuid import UUID

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    status,
)

from sqlalchemy.orm import Session

from app.db.dependencies import get_db

from app.schemas.metric_ingest import (
    MetricIngestRequest,
)

from app.schemas.metric_response import (
    MetricResponse,
)

from app.services.metric_ingestion_service import (
    ingest_metric,
)

from app.services.metric_retrieval_service import (
    get_latest_metric,
    get_metrics,
)
from app.services.metric_mapper import map_fluentbit_metric

# IMPORTANT:
# Yahan apne existing authentication dependency
# ka import use karo.
from app.db.dependencies import (
    get_current_user,
)

router = APIRouter(
    prefix="/metrics",
    tags=["Metrics"],
)


# ==========================================================
# POST /api/metrics/ingest
# ==========================================================

# @router.post(
#     "/ingest",
#     status_code=status.HTTP_201_CREATED,
# )
# def ingest_system_metric(
#     metric: MetricIngestRequest,
#     db: Session = Depends(get_db),
# ):
#     """
#     Receive infrastructure/application metrics
#     from Fluent Bit.
#     """

#     return ingest_metric(
#         db=db,
#         metric_data=metric,
#     )

@router.post("/ingest", status_code=status.HTTP_201_CREATED)
def ingest_system_metric(
    payload: list[dict] | dict,
    db: Session = Depends(get_db),
):
    records = payload if isinstance(payload, list) else [payload]
    results = []
    for raw in records:
        metric_data = map_fluentbit_metric(raw)
        results.append(ingest_metric(db=db, metric_data=metric_data))
    return results


# ==========================================================
# GET /api/metrics/latest
# ==========================================================

@router.get(
    "/latest",
    response_model=MetricResponse,
)
def get_latest_system_metric(
    server_id: UUID | None = Query(None),
    application_id: UUID | None = Query(None),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    Return the latest metric belonging to
    the currently logged-in user's client.
    """

    # ------------------------------------------------------
    # Get client from authenticated user
    # ------------------------------------------------------

    client_id = current_user.client_id

    metric = get_latest_metric(
        db=db,
        client_id=client_id,
        server_id=server_id,
        application_id=application_id,
    )

    if metric is None:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No metrics found",
        )

    return metric


# ==========================================================
# GET /api/metrics
# ==========================================================

@router.get(
    "",
    response_model=list[MetricResponse],
)
def get_system_metrics(
    server_id: UUID | None = Query(None),
    application_id: UUID | None = Query(None),
    start_time: datetime | None = Query(None),
    end_time: datetime | None = Query(None),
    limit: int = Query(
        100,
        ge=1,
        le=1000,
    ),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    Return historical metrics belonging to
    the currently logged-in user's client.
    """

    # ------------------------------------------------------
    # Get client from authenticated user
    # ------------------------------------------------------

    client_id = current_user.client_id

    return get_metrics(
        db=db,
        client_id=client_id,
        server_id=server_id,
        application_id=application_id,
        start_time=start_time,
        end_time=end_time,
        limit=limit,
    )