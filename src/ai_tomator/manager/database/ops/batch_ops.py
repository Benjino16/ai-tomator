from sqlalchemy import func
from sqlalchemy.orm import sessionmaker

from ai_tomator.manager.llm_client.models.response_model import EngineResponse
from ai_tomator.manager.database.ops.user_ops import get_group_id_subquery
from ai_tomator.manager.database.models.batch import (
    Batch,
    BatchFile,
    BatchStatus,
    BatchFileStatus,
    BatchLog,
)
from ai_tomator.manager.database.models.file import File

print("BatchOps using:", Batch.__module__, File.__module__)


class BatchOps:
    def __init__(self, session_local: sessionmaker):
        self.SessionLocal = session_local

    def add(
        self,
        name: str,
        status: BatchStatus,
        files: list[str],
        engine: str,
        endpoint: str,
        file_reader: str,
        prompt: str,
        model: str,
        temperature: float,
        json_format: bool,
        user_id: int,
    ):
        with self.SessionLocal() as session:
            subq = get_group_id_subquery(session, user_id)

            batch = Batch(
                name=name,
                status=status,
                engine=engine,
                endpoint=endpoint,
                prompt=prompt,
                file_reader=file_reader,
                model=model,
                temperature=temperature,
                json_format=json_format,
                user_id=user_id,
                group_id=subq,
            )

            db_files = session.query(File).filter(File.storage_name.in_(files)).all()
            storage_to_id = {f.storage_name: f.id for f in db_files}

            missing = [f for f in files if f not in storage_to_id]
            if missing:
                raise ValueError(f"Files not found in database: {missing}")

            batch.batch_files = [
                BatchFile(
                    file_id=f.id,
                    storage_name=f.storage_name,
                    display_name=f.display_name,
                    status=BatchFileStatus.QUEUED,
                )
                for f in db_files
            ]

            session.add(batch)
            session.commit()
            session.refresh(batch)
            return batch.to_dict()

    def update_status(
        self, batch_id: int, status: BatchStatus, engine_response: EngineResponse = None
    ):
        with self.SessionLocal() as session:
            batch = session.query(Batch).filter_by(id=batch_id).first()
            if not batch:
                raise ValueError(f"Batch id '{batch_id}' not found.")

            if status in Batch.RUNNING_STATUSES and not batch.started_at:
                batch.started_at = func.now()

            if status in Batch.STOPPED_STATUSES and not batch.stopped_at:
                batch.stopped_at = func.now()

            batch.status = status

            if engine_response:
                batch.top_p = engine_response.top_p
                batch.top_k = engine_response.top_k
                batch.max_output_tokens = engine_response.max_output_tokens
                batch.context_window = engine_response.context_window

            session.commit()
            session.refresh(batch)
            return batch.to_dict()

    def update_batch_file_status(
        self,
        batch_id: int,
        storage_name: str,
        status: BatchFileStatus,
        engine_response: EngineResponse = None,
        costs_in_usd: float = None,
    ):
        with self.SessionLocal() as session:
            batch = session.query(Batch).filter_by(id=batch_id).first()
            if not batch:
                raise ValueError(f"Batch id '{batch_id}' not found.")
            batch_file = (
                session.query(BatchFile)
                .filter_by(storage_name=storage_name, batch_id=batch.id)
                .first()
            )
            if not batch_file:
                raise ValueError(f"BatchFile '{storage_name}' not found.")

            batch_file.status = status

            if engine_response:
                batch_file.input = engine_response.input
                batch_file.output = engine_response.output
                batch_file.input_token_count = engine_response.input_tokens
                batch_file.output_token_count = engine_response.output_tokens
                batch_file.seed = engine_response.seed

            if costs_in_usd and batch_file.costs_in_usd is None:
                batch_file.costs_in_usd = costs_in_usd
                batch.costs_in_usd += costs_in_usd

            session.commit()
            session.refresh(batch)
            session.refresh(batch_file)
            return batch_file

    def add_file_log(self, batch_id: int, storage_name: str, log: str):
        with self.SessionLocal() as session:
            batch_file = (
                session.query(BatchFile)
                .filter_by(batch_id=batch_id, storage_name=storage_name)
                .first()
            )
            if not batch_file:
                raise ValueError(
                    f"BatchFile with storage_name '{storage_name}' not found in batch {batch_id}."
                )

        return self.add_batch_log(
            batch_id=batch_id,
            batch_file_id=batch_file.id,
            log=log,
        )

    def add_batch_log(self, batch_id: int, log: str, batch_file_id: int | None = None):
        with self.SessionLocal() as session:
            batch = session.query(Batch).filter_by(id=batch_id).first()
            if not batch:
                raise ValueError(f"Batch id '{batch_id}' not found.")
            if batch_file_id:
                batch_file = (
                    session.query(BatchFile).filter_by(id=batch_file_id).first()
                )
                if not batch_file:
                    raise ValueError(f"BatchFile '{batch_file_id}' not found.")
            batch_log = BatchLog(
                batch_id=batch_id,
                batch_file_id=batch_file_id,
                log=log,
            )
            session.add(batch_log)
            session.commit()
            session.refresh(batch_log)
            return batch_log.to_dict()

    def get(self, batch_id: int, user_id: int) -> dict:
        with self.SessionLocal() as session:
            query = session.query(Batch).filter_by(id=batch_id)
            batch = Batch.accessible_by(query, user_id).first()
            if not batch:
                raise ValueError(f"Batch id '{batch_id}' not found.")
            return batch.to_dict()

    def get_files(self, batch_id: int, user_id: int) -> dict:
        with self.SessionLocal() as session:
            query = session.query(Batch).filter_by(id=batch_id)
            batch = Batch.accessible_by(query, user_id).first()
            if not batch:
                raise ValueError(f"Batch id '{batch_id}' not found.")
            return [bl.to_dict() for bl in batch.batch_files]

    def get_log(self, batch_id: int, user_id: int) -> dict:
        with self.SessionLocal() as session:
            query = session.query(Batch).filter_by(id=batch_id)
            batch = Batch.accessible_by(query, user_id).first()
            if not batch:
                raise ValueError(f"Batch id '{batch_id}' not found.")
            return [bl.to_dict() for bl in batch.batch_logs]

    def list(self, user_id: int):
        with self.SessionLocal() as session:
            batches = Batch.accessible_by(session.query(Batch), user_id).all()
            result = []
            for batch in batches:
                batch_dict = batch.to_dict()

                total_files = len(batch.batch_files)

                processed_files = sum(
                    1 for bf in batch.batch_files if bf.status != BatchFileStatus.QUEUED
                )

                batch_dict["progress"] = f"{processed_files}/{total_files}"
                result.append(batch_dict)
            return result

    def get_active_batches(self):
        with self.SessionLocal() as session:
            query = session.query(Batch).filter_by(status=BatchStatus.FAILED)
            batches = query.filter(Batch.status.in_(Batch.ACTIVE_STATUSES))
            return [b.to_dict() for b in batches]
