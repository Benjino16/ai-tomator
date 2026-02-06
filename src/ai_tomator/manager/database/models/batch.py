import enum

from sqlalchemy import ForeignKey, func, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from ai_tomator.manager.database.base import Base
from .user_group_mixin import UserGroupMixin
from .file import File


class BatchStatus(enum.Enum):
    STARTING = "STARTING"
    RUNNING = "RUNNING"
    STOPPING = "STOPPING"
    STOPPED = "STOPPED"
    FAILED = "FAILED"
    COMPLETED = "COMPLETED"
    SCHEDULED = "SCHEDULED"
    QUEUED = "QUEUED"


class Batch(Base, UserGroupMixin):
    __tablename__ = "batches"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(nullable=False)
    status: Mapped["BatchStatus"] = mapped_column(
        Enum(BatchStatus, name="batch_status_enum"), nullable=False
    )

    engine: Mapped[str] = mapped_column(nullable=False)
    endpoint: Mapped[str] = mapped_column(nullable=False)
    file_reader: Mapped[str] = mapped_column(nullable=False)
    prompt: Mapped[str] = mapped_column(nullable=False)
    model: Mapped[str] = mapped_column(nullable=False)
    temperature: Mapped[float] = mapped_column(nullable=False)

    created_at: Mapped[datetime] = mapped_column(nullable=False, default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        nullable=False, default=func.now(), onupdate=func.now()
    )

    batch_files: Mapped[list["BatchFile"]] = relationship(
        back_populates="batch", cascade="all, delete-orphan"
    )

    batch_logs: Mapped[list["BatchLog"]] = relationship(
        back_populates="batch", cascade="all, delete-orphan"
    )

    def to_dict(self):
        return {c.key: getattr(self, c.key) for c in self.__mapper__.columns}

    ACTIVE_STATUSES = [
        BatchStatus.STARTING,
        BatchStatus.RUNNING,
        BatchStatus.STOPPING,
        BatchStatus.SCHEDULED,
        BatchStatus.QUEUED,
    ]


class BatchFileStatus(enum.Enum):
    QUEUED = "QUEUED"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class BatchFile(Base):
    __tablename__ = "batch_files"

    id: Mapped[int] = mapped_column(primary_key=True)
    batch_id: Mapped[int] = mapped_column(ForeignKey("batches.id"), nullable=False)
    file_id: Mapped[int] = mapped_column(ForeignKey("files.id"), nullable=False)
    storage_name: Mapped[str] = mapped_column(nullable=False)
    display_name: Mapped[str] = mapped_column(nullable=False)
    status: Mapped["BatchFileStatus"] = mapped_column(
        Enum(BatchFileStatus, name="batch_file_status_enum"),
        nullable=False,
        default=BatchFileStatus.QUEUED,
    )

    batch: Mapped["Batch"] = relationship(back_populates="batch_files")
    file: Mapped["File"] = relationship()

    batch_logs: Mapped[list["BatchLog"]] = relationship(back_populates="batch_file")

    def to_dict(self):
        return {c.key: getattr(self, c.key) for c in self.__mapper__.columns}


class BatchLog(Base):
    __tablename__ = "batch_logs"

    id: Mapped[int] = mapped_column(primary_key=True)
    batch_id: Mapped[int] = mapped_column(ForeignKey("batches.id"), nullable=False)
    batch_file_id: Mapped[int] = mapped_column(
        ForeignKey("batch_files.id"), nullable=True
    )
    log: Mapped[str] = mapped_column(nullable=False)
    created_at: Mapped[datetime] = mapped_column(nullable=False, default=func.now())

    batch: Mapped["Batch"] = relationship(back_populates="batch_logs")
    batch_file: Mapped["BatchFile"] = relationship(back_populates="batch_logs")

    def to_dict(self):
        return {c.key: getattr(self, c.key) for c in self.__mapper__.columns}
