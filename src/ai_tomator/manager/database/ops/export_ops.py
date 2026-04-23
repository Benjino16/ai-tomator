from dataclasses import dataclass
from typing import List

from sqlalchemy.orm import sessionmaker, selectinload
from ai_tomator.manager.database.models.batch_task import BatchTaskStatus, BatchTask
from ai_tomator.manager.database.models.batch import (
    Batch,
)
from ai_tomator.manager.database.models.batch_file import BatchFile
from ai_tomator.manager.database.models.endpoint import Endpoint
from ai_tomator.manager.database.models.file import File
from ai_tomator.manager.database.models.prompt import Prompt


@dataclass
class BatchExport:
    batch: Batch
    endpoint: Endpoint
    prompt: Prompt
    files: List[File]
    batch_files: List[BatchFile]
    batch_tasks: List[BatchTask]

class ExportOps:
    def __init__(self, session_local: sessionmaker):
        self.SessionLocal = session_local

    def get_batch_for_export(self, batch_id: int, user_id: int) -> BatchExport:
        with self.SessionLocal() as session:
            query = (
                session.query(Batch)
                .options(
                    selectinload(Batch.batch_files).selectinload(BatchFile.batch_tasks),
                    selectinload(Batch.batch_files).selectinload(BatchFile.file),
                    selectinload(Batch.batch_tasks),
                )
                .filter_by(id=batch_id)
            )

            batch = Batch.accessible_by(query, user_id).first()

            if not batch:
                raise ValueError(f"Batch id '{batch_id}' not found.")

            return BatchExport(
                batch=batch,
                endpoint=batch.endpoint,
                prompt=batch.prompt,
                files=[bf.file for bf in batch.batch_files],
                batch_files=batch.batch_files,
                batch_tasks=batch.batch_tasks,
            )