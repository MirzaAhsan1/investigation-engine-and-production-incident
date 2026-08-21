import uuid

from sqlalchemy import (
    String,
    Boolean,
    ForeignKey,
)

from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from app.db.base import Base
from app.db.base_model import BaseModel


class Server(Base, BaseModel):

    __tablename__ = "servers"

    client_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("clients.id"),
        nullable=False,
        index=True,
    )

    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    host: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    environment: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )

    client = relationship(
        "Client",
        back_populates="servers",
    )

    applications = relationship(
        "Application",
        back_populates="server",
        cascade="all, delete-orphan",
    )