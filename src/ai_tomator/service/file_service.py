from typing import Optional, List
from fastapi import UploadFile
from ..manager.file_manager import FileManager
from ..manager.database import Database


class FileService:
    def __init__(self, db: Database, file_manager: FileManager):
        self.db = db
        self.file_manager = file_manager

    def upload_file(self, file: UploadFile, tags: Optional[List[str]]) -> dict:
        name = self.file_manager.save(file, tags)
        return {"storage_name": name, "status": "uploaded"}

    def list_files(self) -> list[str]:
        return self.db.files.list()

    def delete_file(self, filename: str) -> dict:
        deleted = self.file_manager.delete(filename)
        if not deleted:
            raise FileNotFoundError(f"File '{filename}' not found")
        return {"filename": filename, "status": "deleted"}

    def get_file_path(self, filename: str) -> str:
        return self.file_manager.get_path(filename)
