from sqlalchemy.orm import sessionmaker

from ai_tomator.manager.database.models.batch_file import BatchFile
from ai_tomator.manager.database.models.result import Result, Batch
from ai_tomator.manager.database.ops.user_ops import get_group_id_subquery


class ResultOps:
    def __init__(self, session_local: sessionmaker):
        self.SessionLocal = session_local

    def save(self, batch_id: int, file_id: int):
        with self.SessionLocal() as session:
            batch = session.query(Batch).filter_by(id=batch_id).first()
            if not batch:
                raise ValueError(f"Batch with id '{id}' not found.")

            subq = get_group_id_subquery(session, batch.user_id)
            batch_file = (
                session.query(BatchFile)
                .filter_by(batch_id=batch_id, file_id=file_id)
                .first()
            )
            batch_file_id = batch_file.id

            session.add(
                Result(
                    batch_id=batch_id,
                    batch_file_id=batch_file_id,
                    user_id=batch.user_id,
                    group_id=subq,
                )
            )
            session.commit()

    def list_by_batch(self, batch_id, user_id: int):
        with self.SessionLocal() as session:
            query = session.query(Result).filter_by(batch_id=batch_id)
            results = Result.accessible_by(query, user_id).all()
            return [r.to_dict() for r in results]
