from sqlalchemy import Text, ForeignKey, func, Float, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from ai_tomator.manager.database.base import Base
from .user_group_mixin import UserGroupMixin
from .batch import Batch, File


class Result(Base, UserGroupMixin):
    __tablename__ = "results"

    id: Mapped[int] = mapped_column(primary_key=True)
    batch_id: Mapped[int] = mapped_column(ForeignKey("batches.id"), nullable=False)
    file_id: Mapped[int] = mapped_column(ForeignKey("files.id"), nullable=False)
    display_file_name: Mapped[str] = mapped_column(Text, nullable=False)
    storage_file_name: Mapped[str] = mapped_column(Text, nullable=False)
    input: Mapped[str] = mapped_column(Text, nullable=False)
    output: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(nullable=False, default=func.now())

    engine: Mapped[str] = mapped_column(nullable=False)
    endpoint: Mapped[str] = mapped_column(nullable=False)
    file_reader: Mapped[str] = mapped_column(nullable=False)
    prompt: Mapped[str] = mapped_column(nullable=False)
    model: Mapped[str] = mapped_column(nullable=False)
    temperature: Mapped[float] = mapped_column(nullable=False)

    input_token_count: Mapped[int] = mapped_column(Integer, nullable=False)
    output_token_count: Mapped[int] = mapped_column(Integer, nullable=False)
    top_p: Mapped[float | None] = mapped_column(Float, nullable=True)
    top_k: Mapped[int | None] = mapped_column(Integer, nullable=True)
    max_output_tokens: Mapped[int | None] = mapped_column(Integer, nullable=True)
    seed: Mapped[int | None] = mapped_column(Integer, nullable=True)
    context_window: Mapped[int | None] = mapped_column(Integer, nullable=True)

    user_id: Mapped[int] = mapped_column(nullable=True)
    group_id: Mapped[int] = mapped_column(nullable=True)

    batch: Mapped["Batch"] = relationship()
    file: Mapped["File"] = relationship()

    def to_dict(self):
        return {c.key: getattr(self, c.key) for c in self.__mapper__.columns}
