import uuid

from sqlalchemy import (
    String,
    Boolean,
)

from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from app.db.base import Base
from app.db.base_model import BaseModel


class Client(Base, BaseModel):

    __tablename__ = "clients"

    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        unique=True,
        index=True,
    )

    api_key: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        unique=True,
        index=True,
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )

    servers = relationship(
        "Server",
        back_populates="client",
        cascade="all, delete-orphan",
    )