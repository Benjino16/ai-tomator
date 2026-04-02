import io
from typing import List

from minio import Minio
from .base import FileStorage


class MinIOStorage(FileStorage):
    def __init__(
        self, endpoint: str, access_key: str, secret_key: str, bucket_name: str
    ):
        self.client = Minio(
            endpoint, access_key=access_key, secret_key=secret_key, secure=False
        )
        self.bucket_name = bucket_name
        if not self.client.bucket_exists(bucket_name):
            self.client.make_bucket(bucket_name)

    def upload(self, file_path: str, content: bytes) -> bool:
        try:
            content_io = io.BytesIO(content)
            self.client.put_object(
                self.bucket_name, file_path, content_io, length=len(content)
            )
            return True
        except Exception as e:
            print(f"Upload error: {e}")
            return False

    def download(self, file_path: str) -> bytes:
        try:
            response = self.client.get_object(self.bucket_name, file_path)
            return response.read()
        except Exception as e:
            print(f"Download error: {e}")
            raise

    def delete(self, file_path: str) -> bool:
        try:
            self.client.remove_object(self.bucket_name, file_path)
            return True
        except Exception as e:
            print(f"Delete error: {e}")
            return False

    def exists(self, file_path: str) -> bool:
        try:
            self.client.stat_object(self.bucket_name, file_path)
            return True
        except Exception:
            return False

    def list(self, prefix: str = "") -> List[str]:
        try:
            objects = self.client.list_objects(
                self.bucket_name, prefix=prefix, recursive=True
            )
            return [obj.object_name for obj in objects]
        except Exception as e:
            print(f"List error: {e}")
            return []
