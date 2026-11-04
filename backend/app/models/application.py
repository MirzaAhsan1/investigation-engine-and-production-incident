import uuid

from sqlalchemy import (
    String,
    Boolean,
    ForeignKey,
    DateTime
)
from datetime import datetime

from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from app.db.base import Base
from app.db.base_model import BaseModel


class Application(Base, BaseModel):

    __tablename__ = "applications"

    server_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("servers.id"),
        nullable=False,
        index=True,
    )

    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    container_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    provider: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    resource_uuid: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )

    server = relationship(
        "Server",
        back_populates="applications",
    )
    last_known_deployment_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )