from __future__ import annotations
from typing import TYPE_CHECKING
from sqlalchemy import Text, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from ai_tomator.manager.database.base import Base

if TYPE_CHECKING:
    from .group import Group


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(Text, nullable=False)
    password_hash: Mapped[str] = mapped_column(Text, nullable=False)
    group_id: Mapped[int] = mapped_column(ForeignKey("groups.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(nullable=False, default=func.now())

    group: Mapped["Group"] = relationship(back_populates="users")

    def to_dict_internal(self):
        return {c.key: getattr(self, c.key) for c in self.__mapper__.columns}

    def to_dict_public(self):
        data = self.to_dict_internal()
        data.pop("password_hash", None)
        return data
