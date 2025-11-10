from sqlalchemy import Text, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from ai_tomator.manager.database.base import Base
from .base_mixins import RunDataMixin
from .batch import Batch, File

class Result(Base, RunDataMixin):
    __tablename__ = "results"

    id: Mapped[int] = mapped_column(primary_key=True)
    batch_id: Mapped[int] = mapped_column(ForeignKey("batches.id"), nullable=False)
    file_id: Mapped[int] = mapped_column(ForeignKey("files.id"), nullable=False)
    file_name: Mapped[str] = mapped_column(nullable=False)
    input: Mapped[str] = mapped_column(Text, nullable=False)
    output: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(nullable=False, default=func.now())

    batch: Mapped["Batch"] = relationship()
    file: Mapped["File"] = relationship()

    def to_dict(self):
        return {c.key: getattr(self, c.key) for c in self.__mapper__.columns}
