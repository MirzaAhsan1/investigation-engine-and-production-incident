from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.enums.analysis_status import AnalysisStatusEnum
from app.schemas.action_queue import ActionResponse


class InvestigationCreate(BaseModel):
    incident_id: UUID


class InvestigationResponse(BaseModel):

    id: UUID

    incident_id: UUID

    # ==========================
    # ML Prediction
    # ==========================

    predicted_category: str

    predicted_cause: str

    confidence: float

    model_version: str | None

    # ==========================
    # Risk
    # ==========================

    risk_score: float

    # ==========================
    # LLM Analysis
    # ==========================

    root_cause: str | None

    reasoning: str | None

    recommended_actions: str | None

    llm_confidence: float | None

    # ==========================
    # Rule Engine
    # ==========================

    triggered_rules: list[str] | None

    # ==========================
    # Status
    # ==========================

    analysis_status: AnalysisStatusEnum

    # ==========================
    # Actions
    # ==========================

    actions: list[ActionResponse] = []

    # ==========================
    # Audit
    # ==========================

    created_at: datetime

    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
    )