from sqlalchemy.orm import sessionmaker
from ai_tomator.manager.database.models.file import File


class FileOps:
    def __init__(self, session_local: sessionmaker):
        self.SessionLocal = session_local

    def add(
        self,
        storage_name: str,
        display_name: str,
        tags: list[str],
        mime_type: str,
        size: int,
    ):
        with self.SessionLocal() as session:
            file = File(
                storage_name=storage_name,
                display_name=display_name,
                tags=tags,
                mime_type=mime_type,
                size=size,
            )
            session.add(file)
            session.commit()
            return file.to_dict()

    def get(self, storage_name: str):
        with self.SessionLocal() as session:
            file = session.query(File).filter_by(storage_name=storage_name).first()
            if not file:
                raise ValueError(f"File '{storage_name}' not found.")
            return file.to_dict()

    def list(self):
        with self.SessionLocal() as session:
            return [f.to_dict() for f in session.query(File).all()]

    def delete(self, storage_name: str):
        with self.SessionLocal() as session:
            file = session.query(File).filter_by(storage_name=storage_name).first()
            if not file:
                raise ValueError(f"File '{storage_name}' not found.")
            session.delete(file)
            session.commit()
            return file.to_dict()
