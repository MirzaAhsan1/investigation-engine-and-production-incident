import uuid

from sqlalchemy import (
    Enum,
    ForeignKey,
    String,
    Text,
    Boolean
)

from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from app.db.base import Base
from app.db.base_model import BaseModel

from app.models.enums import (
    IncidentSourceEnum,
    IncidentTypeEnum,
    SeverityEnum,
    StatusEnum,
)


class Incident(Base, BaseModel):

    __tablename__ = "incidents"

    # ==========================================================
    # Basic Incident Information
    # ==========================================================

    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    description: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    incident_type: Mapped[IncidentTypeEnum] = mapped_column(
        Enum(IncidentTypeEnum),
        nullable=False,
    )

    severity: Mapped[SeverityEnum] = mapped_column(
        Enum(SeverityEnum),
        nullable=False,
        default=SeverityEnum.MEDIUM,
    )

    status: Mapped[StatusEnum] = mapped_column(
        Enum(StatusEnum),
        nullable=False,
        default=StatusEnum.OPEN,
    )

    source: Mapped[IncidentSourceEnum] = mapped_column(
        Enum(IncidentSourceEnum),
        nullable=False,
        default=IncidentSourceEnum.MANUAL,
    )

    # ==========================================================
    # Users
    # ==========================================================

    reported_by: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
        index=True,
    )

    assigned_to: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("users.id"),
        nullable=True,
        index=True,
    )

    reporter = relationship(
        "User",
        foreign_keys=[reported_by],
    )

    assignee = relationship(
        "User",
        foreign_keys=[assigned_to],
    )

    # ==========================================================
    # Application / Container
    # ==========================================================

    application_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("applications.id"),
        nullable=True,
        index=True,
    )

    application = relationship(
        "Application",
        foreign_keys=[application_id],
    )

    # ==========================================================
    # Correlation Groups
    # ==========================================================

    correlation_groups = relationship(
        "CorrelationGroup",
        back_populates="incident",
    )

    # ==========================================================
    # Investigation
    # ==========================================================

    investigation = relationship(
        "Investigation",
        back_populates="incident",
        uselist=False,
    )

    # ==========================================================
    # Evidence
    # ==========================================================

    evidence = relationship(
        "Evidence",
        back_populates="incident",
        # uselist=False,
    )

    created_by_system: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
    )