from datetime import datetime
from uuid import UUID

from pydantic import BaseModel
from pydantic import ConfigDict


class ApplicationCreate(BaseModel):

    server_id: UUID

    name: str

    container_name: str

    provider: str

    resource_uuid: str | None = None


class ApplicationResponse(BaseModel):

    id: UUID

    server_id: UUID

    name: str

    container_name: str

    provider: str

    resource_uuid: str | None

    is_active: bool

    created_at: datetime

    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
    )