from pydantic import BaseModel


class FileData(BaseModel):
    display_name: str
    storage_name: str
    size: int | None
    mime_type: str | None
