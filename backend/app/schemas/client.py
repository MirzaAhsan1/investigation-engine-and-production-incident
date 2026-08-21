from datetime import datetime
from uuid import UUID

from pydantic import BaseModel
from pydantic import ConfigDict


class ClientCreate(BaseModel):

    name: str

    api_key: str


class ClientResponse(BaseModel):

    id: UUID

    name: str

    api_key: str

    is_active: bool

    created_at: datetime

    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
    )