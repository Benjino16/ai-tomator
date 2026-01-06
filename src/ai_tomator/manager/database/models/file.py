from sqlalchemy import JSON, func
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime
from ai_tomator.manager.database.base import Base


class File(Base):
    __tablename__ = "files"

    id: Mapped[int] = mapped_column(primary_key=True)
    display_name: Mapped[str] = mapped_column(nullable=False)
    storage_name: Mapped[str] = mapped_column(nullable=False, unique=True)
    tags: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    mime_type: Mapped[str | None] = mapped_column(nullable=True)
    size: Mapped[int | None] = mapped_column(nullable=True)
    created_at: Mapped[datetime] = mapped_column(nullable=False, default=func.now())

    owner_id: Mapped[int] = mapped_column(nullable=False)
    group_id: Mapped[int] = mapped_column(nullable=True)

    def to_dict(self):
        return {c.key: getattr(self, c.key) for c in self.__mapper__.columns}
