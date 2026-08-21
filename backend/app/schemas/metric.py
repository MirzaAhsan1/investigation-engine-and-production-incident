from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class MetricIngestRequest(BaseModel):

    client_id: UUID
    server_id: UUID
    application_id: UUID

    timestamp: datetime

    cpu_usage: float | None = None
    memory_usage: float | None = None


class MetricIngestResponse(BaseModel):

    model_config = ConfigDict(
        from_attributes=True,
    )

    id: UUID

    client_id: UUID
    server_id: UUID
    application_id: UUID

    timestamp: datetime

    cpu_usage: float | None
    memory_usage: float | None

    created_at: datetime
    updated_at: datetime