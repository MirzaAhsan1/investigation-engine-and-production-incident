from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.db.base_model import BaseModel


class User(Base, BaseModel):

    __tablename__ = "users"

    full_name: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
    )

    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        index=True,
        nullable=False,
    )

    password_hash: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    reported_incidents = relationship(
        "Incident",
        foreign_keys="Incident.reported_by",
        back_populates="reporter",
    )

    assigned_incidents = relationship(
        "Incident",
        foreign_keys="Incident.assigned_to",
        back_populates="assignee",
    )