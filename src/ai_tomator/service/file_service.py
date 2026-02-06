from typing import Optional, List
from fastapi import UploadFile
from ..manager.file_manager import FileManager
from ..manager.database import Database


class FileService:
    def __init__(self, db: Database, file_manager: FileManager):
        self.db = db
        self.file_manager = file_manager

    def upload_file(
        self, file: UploadFile, tags: Optional[List[str]], user_id: int
    ) -> dict:
        return self.file_manager.save(file, tags, user_id)

    def list_files(self, user_id: int) -> list[dict]:
        return self.db.files.list(user_id)

    def delete_file(self, filename: str, user_id: int) -> dict:
        deleted = self.file_manager.delete(filename, user_id)
        if not deleted:
            raise FileNotFoundError(f"File '{filename}' not found")
        return {"filename": filename, "status": "deleted"}

    def get_file_path(self, filename: str) -> str:
        return self.file_manager.get_path(filename)
