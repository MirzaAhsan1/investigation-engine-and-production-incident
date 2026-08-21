from datetime import datetime
from uuid import UUID

from pydantic import BaseModel
from pydantic import ConfigDict


class ServerCreate(BaseModel):

    client_id: UUID

    name: str

    host: str

    environment: str


class ServerResponse(BaseModel):

    id: UUID

    client_id: UUID

    name: str

    host: str

    environment: str

    is_active: bool

    created_at: datetime

    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
    )