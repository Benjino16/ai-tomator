from pydantic import BaseModel


class FileData(BaseModel):
    id: int
    name: str
    size: int | None
    mime_type: str | None
    tags: list[str] | None = None
