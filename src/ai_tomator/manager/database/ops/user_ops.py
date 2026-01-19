from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import sessionmaker
from ai_tomator.core.exceptions import NameAlreadyExistsError
from ai_tomator.manager.database.models.user import User


class UserOps:
    def __init__(self, session_local: sessionmaker):
        self.SessionLocal = session_local

    def add(self, username: str, password_hash: str):
        with self.SessionLocal() as session:
            user = User(username=username, password_hash=password_hash)
            session.add(user)
            try:
                session.commit()
            except IntegrityError:
                session.rollback()
                raise NameAlreadyExistsError(username)

    def get_for_verification(self, username: str):
        with self.SessionLocal() as session:
            user = session.query(User).filter_by(username=username).first()
            if not user:
                raise ValueError(f"User '{username}' not found.")
            return user.to_dict_internal()

    def get_by_username(self, username: str):
        with self.SessionLocal() as session:
            user = session.query(User).filter_by(username=username).first()
            if user:
                return user.to_dict_public()
            return None

    def list(self):
        with self.SessionLocal() as session:
            return [e.to_dict_public() for e in session.query(User).all()]
