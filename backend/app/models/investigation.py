import uuid

from sqlalchemy import (
    Enum,
    Float,
    ForeignKey,
    JSON,
    String,
    Text,
)

from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from app.db.base import Base
from app.db.base_model import BaseModel
from app.enums.analysis_status import AnalysisStatusEnum


class Investigation(Base, BaseModel):

    __tablename__ = "investigations"

    incident_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("incidents.id"),
        nullable=False,
        unique=True,
    )

    # ==========================
# ML Prediction
# ==========================

    predicted_category: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    predicted_cause: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    confidence: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    model_version: Mapped[str | None] = mapped_column(
        String(30),
        nullable=True,
    )

    # ==========================
    # Overall Risk
    # ==========================

    risk_score: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    # ==========================
    # LLM Analysis
    # ==========================

    root_cause: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    reasoning: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    recommended_actions: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    llm_confidence: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    # ==========================
    # Rule Engine
    # ==========================

    triggered_rules: Mapped[list | None] = mapped_column(
        JSON,
        nullable=True,
    )

    # ==========================
    # Status
    # ==========================

    analysis_status: Mapped[AnalysisStatusEnum] = mapped_column(
        Enum(AnalysisStatusEnum),
        default=AnalysisStatusEnum.PENDING,
        nullable=False,
    )

    # ==========================
    # Relationships
    # ==========================

    incident = relationship(
        "Incident",
        back_populates="investigation",
    )

    actions = relationship(
        "ActionQueue",
        back_populates="investigation",
        cascade="all, delete-orphan",
        lazy="selectin",
    )