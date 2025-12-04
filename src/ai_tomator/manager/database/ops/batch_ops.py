from sqlalchemy.orm import sessionmaker
from ai_tomator.manager.database.models.batch import Batch, BatchFile, BatchStatus, BatchFileStatus
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
    ):
        with self.SessionLocal() as session:
            batch = Batch(
                name=name,
                status=status,
                engine=engine,
                endpoint=endpoint,
                prompt=prompt,
                file_reader=file_reader,
                model=model,
                temperature=temperature,
            )

            db_files = session.query(File).filter(File.storage_name.in_(files)).all()
            storage_to_id = {f.storage_name: f.id for f in db_files}

            missing = [f for f in files if f not in storage_to_id]
            if missing:
                raise ValueError(f"Files not found in database: {missing}")

            batch.batch_files = [
                BatchFile(file_id=storage_to_id[f], storage_name=f, status="pending")
                for f in files
            ]

            session.add(batch)
            session.commit()
            session.refresh(batch)
            return batch.to_dict()

    def update_status(self, batch_id: int, status: BatchStatus):
        with self.SessionLocal() as session:
            batch = session.query(Batch).filter_by(id=batch_id).first()
            if not batch:
                raise ValueError(f"Batch id '{batch_id}' not found.")
            batch.status = status
            session.commit()
            session.refresh(batch)
            return batch.to_dict()

    def update_batch_file_status(self, batch_id: int, storage_name: str, status: BatchFileStatus):
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
            session.commit()
            session.refresh(batch)
            session.refresh(batch_file)
            return batch.to_dict()

    def get(self, batch_id: int) -> dict:
        with self.SessionLocal() as session:
            batch = session.query(Batch).filter_by(id=batch_id).first()
            if not batch:
                raise ValueError(f"Batch id '{batch_id}' not found.")
            return batch.to_dict()

    def list(self, status: BatchStatus = None):
        with self.SessionLocal() as session:
            query = session.query(Batch)
            if status:
                query = query.filter(Batch.status == status)
            return [b.to_dict() for b in query.all()]
