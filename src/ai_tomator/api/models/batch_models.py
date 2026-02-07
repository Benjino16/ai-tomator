from datetime import datetime

from pydantic import BaseModel, Field
from typing import List, Optional


# -----      requests      -----
class BatchRunRequest(BaseModel):
    prompt_id: int
    files: List[str]
    endpoint: str
    file_reader: str
    model: str
    delay: float = Field(..., ge=0, le=10000)
    temperature: float = Field(..., ge=0.0, le=3.0)


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
    started_at: Optional[datetime]
    stopped_at: Optional[datetime]
