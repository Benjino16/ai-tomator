from datetime import datetime

from pydantic import BaseModel
from typing import List


# -----      requests      -----
class BatchRunRequest(BaseModel):
    prompt_id: int
    files: List[str]
    endpoint: str
    file_reader: str
    model: str
    delay: float
    temperature: float


# -----      data      -----
class BatchData(BaseModel):
    id: int
    name: str
    status: str
    prompt: str
    # todo: files
    endpoint: str
    file_reader: str
    model: str
    # todo: delay
    temperature: float
    created_at: datetime
    updated_at: datetime
