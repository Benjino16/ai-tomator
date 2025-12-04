from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import sessionmaker
from ai_tomator.core.exceptions import NameAlreadyExistsError
from ai_tomator.manager.database.models.prompt import Prompt


class PromptOps:
    def __init__(self, session_local: sessionmaker):
        self.SessionLocal = session_local

    def add(self, name: str, prompt: str) -> dict:
        with self.SessionLocal() as session:
            pr = Prompt(name=name, prompt=prompt)
            session.add(pr)
            try:
                session.commit()
                session.refresh(pr)
                return pr.to_dict()
            except IntegrityError:
                session.rollback()
                raise NameAlreadyExistsError(name)

    def list(self) -> list[dict]:
        with self.SessionLocal() as session:
            return [p.to_dict() for p in session.query(Prompt).all()]

    def delete(self, prompt_id: int) -> dict:
        with self.SessionLocal() as session:
            pr = session.query(Prompt).filter_by(id=prompt_id).first()
            if not pr:
                raise ValueError(f"Prompt with ID {prompt_id} not found.")
            session.delete(pr)
            session.commit()
            return pr.to_dict()
