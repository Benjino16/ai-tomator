import io
import os
import uuid
from typing import BinaryIO

from fastapi import UploadFile
from ai_tomator.manager.database import Database
from .file_storage import FileStorage


class FileManager:
    def __init__(self, storage: FileStorage, db: Database):
        self.storage = storage
        self.db = db

    def _unique_name(self, original_name: str) -> str:
        base, ext = os.path.splitext(original_name)
        return f"{uuid.uuid4().hex[:8]}{ext}"

    def upload(self, file: UploadFile, tags: list[str], user_id: int):
        unique_name = self._unique_name(file.filename)

        content = file.file.read()
        if not self.storage.upload(unique_name, content):
            return None

        file_record = self.db.files.add(
            name=file.filename,
            path=unique_name,
            tags=tags,
            mime_type=file.content_type,
            size=file.size,
            user_id=user_id,
        )

        return file_record

    def download(self, file_id: int, user_id: int) -> BinaryIO:
        file_record = self.db.files.get(file_id, user_id)
        if not file_record:
            raise ValueError("File does not exist or user has no permissions!")

        file_path = file_record.path
        bytes_data = self.storage.download(file_path)
        binary_io = io.BytesIO(bytes_data)
        binary_io.name = file_record.name
        return binary_io

    def download_by_path(self, path: str) -> BinaryIO:
        if not self.storage.exists(path):
            raise ValueError("File does not exist!")
        bytes_data = self.storage.download(path)
        return io.BytesIO(bytes_data)


    def delete(self, file_id: int, user_id: int) -> bool:
        file_record = self.db.files.get(file_id, user_id)
        if not file_record:
            return False

        file_path = file_record.path

        if self.storage.delete(file_path):
            self.db.files.delete(file_id, user_id)
            return True
        return False

    def list(self) -> list[str]:
        return self.storage.list()

    def sync_storage_with_db(self):
        storage_files = self.list()
        db_files = self.db.files.system_list()
        db_storage_names = {f["storage_name"] for f in db_files}

        # check files in storage; if not in db: add
        for file in storage_files:
            if file not in db_storage_names:
                # todo: rename file?
                # todo: contenttype und size possible null reference
                self.db.files.add(
                    name=file,
                    path=file,
                    tags=None,
                    mime_type="test",
                    size=0,
                    user_id=0,
                )

        for db_file in db_storage_names:
            if db_file not in storage_files:
                self.db.files.set_storage_status(path=db_file, in_storage=False)
