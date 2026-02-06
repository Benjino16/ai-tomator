from sqlalchemy.orm import sessionmaker
from ai_tomator.manager.database.models.file import File
from ai_tomator.manager.database.ops.user_ops import get_group_id_subquery


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
        user_id: int,
    ):
        with self.SessionLocal() as session:

            subq = get_group_id_subquery(session, user_id)

            file = File(
                storage_name=storage_name,
                display_name=display_name,
                tags=tags,
                mime_type=mime_type,
                size=size,
                user_id=user_id,
                group_id=subq,
            )
            session.add(file)
            session.commit()
            return file.to_dict()

    def get(self, storage_name: str, user_id: int):
        with self.SessionLocal() as session:
            query = session.query(File).filter_by(storage_name=storage_name)
            file = File.accessible_by(query, user_id).first()
            if not file:
                raise ValueError(f"File '{storage_name}' not found.")
            return file.to_dict()

    def list(self, user_id: int):
        with self.SessionLocal() as session:
            query = session.query(File)
            files = File.accessible_by(query, user_id).all()
            return [f.to_dict() for f in files]

    def system_list(self):
        with self.SessionLocal() as session:
            files = session.query(File).all()
            return [f.to_dict() for f in files]

    def delete(self, storage_name: str, user_id: int):
        with self.SessionLocal() as session:
            query = session.query(File).filter_by(storage_name=storage_name)
            file = File.accessible_by(query, user_id).first()
            if not file:
                raise ValueError(f"File '{storage_name}' not found.")
            session.delete(file)
            session.commit()
            return file.to_dict()

    def set_storage(self, storage_name: str, in_storage: bool):
        with self.SessionLocal() as session:
            file = session.query(File).filter_by(storage_name=storage_name).first()
            if not file:
                raise ValueError(f"File '{storage_name}' not found.")
            file.in_storage = in_storage
            session.commit()
            session.refresh(file)
            return file.to_dict()