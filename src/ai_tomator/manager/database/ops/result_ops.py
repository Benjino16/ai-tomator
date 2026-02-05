from sqlalchemy.orm import sessionmaker

from ai_tomator.core.engine.models.response_model import EngineResponse
from ai_tomator.manager.database.models.result import Result, Batch, File
from ai_tomator.manager.database.ops.user_ops import get_group_id_subquery


class ResultOps:
    def __init__(self, session_local: sessionmaker):
        self.SessionLocal = session_local

    def save(
        self, batch_id: int, storage_file_name: str, engine_response: EngineResponse
    ):
        with self.SessionLocal() as session:
            batch = session.query(Batch).filter_by(id=batch_id).first()
            if not batch:
                raise ValueError(f"Batch with id '{id}' not found.")

            subq = get_group_id_subquery(session, batch.user_id)
            file = session.query(File).filter_by(storage_name=storage_file_name).first()
            file_id = file.id
            file_display_name = file.display_name

            session.add(
                Result(
                    batch_id=batch_id,
                    file_id=file_id,
                    display_file_name=file_display_name,
                    storage_file_name=storage_file_name,
                    input=engine_response.input,
                    output=engine_response.output,
                    engine=batch.engine,
                    endpoint=batch.endpoint,
                    file_reader=batch.file_reader,
                    prompt=batch.prompt,
                    model=batch.model,
                    temperature=batch.temperature,
                    top_p=engine_response.top_p,
                    top_k=engine_response.top_k,
                    max_output_tokens=engine_response.max_output_tokens,
                    seed=engine_response.seed,
                    context_window=engine_response.context_window,
                    input_token_count=engine_response.input_tokens,
                    output_token_count=engine_response.output_tokens,
                    user_id=batch.user_id,
                    group_id=subq,
                )
            )
            session.commit()

    def list_by_batch(self, batch_id):
        with self.SessionLocal() as session:
            rows = session.query(Result).filter_by(batch_id=batch_id).all()
            return [r.to_dict() for r in rows]
