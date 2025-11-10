from sqlalchemy.orm import sessionmaker
from ai_tomator.manager.database.models.result import Result, Batch, File


class ResultOps:
    def __init__(self, session_local: sessionmaker):
        self.SessionLocal = session_local

    def save(self, batch_id: int, file_name: str, input: str, output: str):
        with self.SessionLocal() as session:
            batch = session.query(Batch).filter_by(id=batch_id).first()
            if not batch:
                raise ValueError(f"Batch with id '{id}' not found.")
            file_id = session.query(File).filter_by(storage_name=file_name).first().id

            session.add(
                Result(
                    batch_id=batch_id,
                    file_id=file_id,
                    file_name=file_name,
                    input=input,
                    output=output,
                    engine=batch.engine,
                    endpoint=batch.endpoint,
                    file_reader=batch.file_reader,
                    prompt=batch.prompt,
                    model=batch.model,
                    temperature=batch.temperature,
                )
            )
            session.commit()

    def list_by_batch(self, batch_id):
        with self.SessionLocal() as session:
            rows = session.query(Result).filter_by(batch_id=batch_id).all()
            return [r.to_dict() for r in rows]
