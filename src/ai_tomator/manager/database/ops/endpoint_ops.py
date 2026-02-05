from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import sessionmaker
from ai_tomator.core.exceptions import NameAlreadyExistsError
from ai_tomator.manager.database.models.endpoint import Endpoint
from ai_tomator.manager.database.ops.user_ops import get_group_id_subquery


class EndpointOps:
    def __init__(self, session_local: sessionmaker):
        self.SessionLocal = session_local

    def add(self, name: str, engine: str, user_id: int, url=None, token=None):
        with self.SessionLocal() as session:
            subq = get_group_id_subquery(session, user_id)
            ep = Endpoint(
                name=name,
                engine=engine,
                url=url,
                token=token,
                user_id=user_id,
                group_id=subq,
            )
            session.add(ep)
            try:
                session.commit()
            except IntegrityError:
                session.rollback()
                raise NameAlreadyExistsError(name)

    def get(self, name: str, show_api=False):
        with self.SessionLocal() as session:
            ep = session.query(Endpoint).filter_by(name=name).first()
            if not ep:
                raise ValueError(f"Endpoint '{name}' not found.")
            if show_api:
                return ep.to_dict_internal()
            else:
                return ep.to_dict_public()

    def list(self):
        with self.SessionLocal() as session:
            return [e.to_dict_public() for e in session.query(Endpoint).all()]

    def delete(self, name: str):
        with self.SessionLocal() as session:
            ep = session.query(Endpoint).filter_by(name=name).first()
            if not ep:
                raise ValueError(f"Endpoint '{name}' not found.")
            session.delete(ep)
            session.commit()
