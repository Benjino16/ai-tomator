import os
import shutil
import uuid
from fastapi import UploadFile
from ai_tomator.manager.database import Database


class FileManager:
    def __init__(self, storage_dir: str, db: Database):
        self.storage_dir = os.path.abspath(storage_dir)
        self.db = db
        os.makedirs(self.storage_dir, exist_ok=True)

    def _unique_name(self, original_name: str) -> str:
        base, ext = os.path.splitext(original_name)
        return f"{uuid.uuid4().hex[:8]}{ext}"

    def save(self, file: UploadFile, tags: list[str], user_id: int):
        unique_name = self._unique_name(file.filename)
        dest_path = os.path.join(self.storage_dir, unique_name)
        with open(dest_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        file = self.db.files.add(
            unique_name, file.filename, tags, file.content_type, file.size, user_id
        )  # todo: contenttype und size possible null reference
        return file

    def delete(self, filename: str) -> bool:
        path = os.path.join(self.storage_dir, filename)
        if os.path.exists(path):
            os.remove(path)
            self.db.files.delete(filename)
            return True
        return False

    def list_files(self) -> list[str]:
        return sorted(os.listdir(self.storage_dir))

    def get_path(self, filename: str) -> str:
        path = os.path.join(self.storage_dir, filename)
        if not os.path.exists(path):
            raise FileNotFoundError(f"File '{filename}' not found.")
        return path

    def sync_storage_with_db(self):
        storage_files = self.list_files()
        db_files = self.db.files.list()
        db_storage_names = {f["storage_name"] for f in db_files}

        # check files in storage; if not in db: add
        for file in storage_files:
            if file not in db_storage_names:
                # todo: rename file?
                # todo: contenttype und size possible null reference
                self.db.files.add(
                    storage_name=file,
                    display_name=file,
                    tags=None,
                    mime_type="test",
                    size=0,
                    user_id=0,
                )

        # check files in db; if not in storage: delete
        for db_file in db_storage_names:
            if db_file not in storage_files:
                self.db.files.delete(storage_name=db_file)
