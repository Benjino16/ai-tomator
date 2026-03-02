from sqlalchemy import ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from ai_tomator.manager.database.base import Base
from .user_group_mixin import UserGroupMixin
from .batch import Batch, BatchFile


class Result(Base, UserGroupMixin):
    __tablename__ = "results"

    id: Mapped[int] = mapped_column(primary_key=True)
    batch_id: Mapped[int] = mapped_column(ForeignKey("batches.id"), nullable=False)
    batch_file_id: Mapped[int] = mapped_column(
        ForeignKey("batch_files.id"), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(nullable=False, default=func.now())

    user_id: Mapped[int] = mapped_column(nullable=True)
    group_id: Mapped[int] = mapped_column(nullable=True)

    batch: Mapped["Batch"] = relationship(lazy="joined")
    batch_file: Mapped["BatchFile"] = relationship(lazy="joined")

    def to_dict(self):
        result_dict = {c.key: getattr(self, c.key) for c in self.__mapper__.columns}

        result_dict.update(
            {
                "display_file_name": self.batch_file.display_name,
                "storage_file_name": self.batch_file.storage_name,
                "input_token_count": self.batch_file.input_token_count,
                "output_token_count": self.batch_file.output_token_count,
                "input": self.batch_file.input,
                "output": self.batch_file.output,
                "seed": self.batch_file.seed,
                "engine": self.batch.engine,
                "endpoint": self.batch.endpoint,
                "file_reader": self.batch.file_reader,
                "prompt": self.batch.prompt,
                "model": self.batch.model,
                "temperature": self.batch.temperature,
                "json_format": self.batch.json_format,
                "top_p": self.batch.top_p,
                "top_k": self.batch.top_k,
                "max_output_tokens": self.batch.max_output_tokens,
                "context_window": self.batch.context_window,
                "costs_in_USD": self.batch_file.costs_in_usd,
            }
        )
        return result_dict
