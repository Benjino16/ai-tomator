from sqlalchemy import ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from ai_tomator.manager.database.base import Base
from .base_mixins import RunDataMixin
from .file import File


class Batch(Base, RunDataMixin):
    __tablename__ = "batches"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(nullable=False)
    status: Mapped[str] = mapped_column(nullable=False)
    created_at: Mapped[datetime] = mapped_column(nullable=False, default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        nullable=False, default=func.now(), onupdate=func.now()
    )

    batch_files: Mapped[list["BatchFile"]] = relationship(
        back_populates="batch", cascade="all, delete-orphan"
    )

    def to_dict(self):
        return {c.key: getattr(self, c.key) for c in self.__mapper__.columns}


class BatchFile(Base):
    __tablename__ = "batch_files"

    id: Mapped[int] = mapped_column(primary_key=True)
    batch_id: Mapped[int] = mapped_column(ForeignKey("batches.id"), nullable=False)
    file_id: Mapped[int] = mapped_column(ForeignKey("files.id"), nullable=False)
    storage_name: Mapped[str] = mapped_column(nullable=False)
    status: Mapped[str] = mapped_column(nullable=False, default="pending")

    batch: Mapped["Batch"] = relationship(back_populates="batch_files")
    file: Mapped["File"] = relationship()

    def to_dict(self):
        return {c.key: getattr(self, c.key) for c in self.__mapper__.columns}
