import uuid

from sqlalchemy import (
    Enum,
    Float,
    ForeignKey,
    Integer,
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

from app.enums.action_status import ActionStatusEnum


class ActionQueue(Base, BaseModel):

    __tablename__ = "action_queue"

    investigation_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("investigations.id"),
        nullable=False,
        index=True,
    )

    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    action_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    target: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    priority: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    confidence: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    status: Mapped[ActionStatusEnum] = mapped_column(
        Enum(ActionStatusEnum),
        default=ActionStatusEnum.PENDING,
        nullable=False,
    )

    approved_by: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("users.id"),
        nullable=True,
    )

    execution_log: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    investigation = relationship(
        "Investigation",
        back_populates="actions",
    )
    provider: Mapped[str] = mapped_column(

        String(50),

        nullable=False,

        default="coolify",
    )