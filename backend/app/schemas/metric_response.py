from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class MetricResponse(BaseModel):

    id: UUID

    client_id: UUID
    server_id: UUID
    application_id: UUID

    timestamp: datetime

    cpu_usage: float | None = None
    memory_usage: float | None = None

    disk_usage: float | None = None
    disk_io_wait: float | None = None

    api_latency: float | None = None

    http_5xx_count: int | None = None
    http_4xx_count: int | None = None

    request_per_second: float | None = None

    class Config:
        from_attributes = True