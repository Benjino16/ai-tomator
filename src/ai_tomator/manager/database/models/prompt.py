from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import func
from datetime import datetime

from ai_tomator.manager.database.base import Base


class Prompt(Base):
    __tablename__ = "prompts"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(unique=True, nullable=False)
    content: Mapped[str] = mapped_column(nullable=False)

    created_at: Mapped[datetime] = mapped_column(nullable=False, default=func.now())

    owner_id: Mapped[int] = mapped_column(nullable=True)
    group_id: Mapped[int] = mapped_column(nullable=True)

    def to_dict(self):
        return {c.key: getattr(self, c.key) for c in self.__mapper__.columns}
