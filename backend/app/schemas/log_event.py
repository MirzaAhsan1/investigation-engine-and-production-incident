from uuid import UUID
from datetime import datetime
from typing import Optional
from app.enums.log_status import LogStatusEnum
from pydantic import BaseModel
from pydantic import ConfigDict


class LogEventResponse(BaseModel):

    id: UUID

    application: str

    host: str

    level: str

    message: str

    timestamp: datetime

    status: LogStatusEnum

    created_at: datetime

    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
    )


class LogEventListItem(BaseModel):
    """
    Response schema for the GET /api/logs endpoint.

    Includes fields from log_events plus
    resolved names from related application/server.
    """

    id: UUID

    level: str

    message: str

    timestamp: datetime

    status: str

    occurrence_count: int

    first_seen: datetime

    last_seen: datetime

    fingerprint: str

    correlation_group_id: Optional[UUID] = None

    # Resolved from relationships
    container_name: Optional[str] = None

    host: Optional[str] = None

    application_name: Optional[str] = None

    server_name: Optional[str] = None

    created_at: datetime

    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
    )