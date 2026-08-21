from datetime import datetime
from uuid import UUID

from pydantic import BaseModel
from pydantic import ConfigDict

from app.enums.action_status import ActionStatusEnum


class ActionResponse(BaseModel):

    id: UUID

    investigation_id: UUID

    title: str

    action_type: str

    target: str

    priority: int

    confidence: float

    status: ActionStatusEnum

    provider: str

    approved_by: UUID | None

    execution_log: str | None

    created_at: datetime

    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
    )


class ApproveActionRequest(BaseModel):

    approved_by: UUID | None = None


class RejectActionRequest(BaseModel):

    approved_by: UUID | None = None