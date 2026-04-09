from datetime import datetime

from pydantic import BaseModel, Field
from typing import List, Optional


# -----      requests      -----
class BatchRunRequest(BaseModel):
    prompt_id: int
    files: List[int]
    endpoint: str
    file_reader: str
    model: str
    delay: float = Field(..., ge=0, le=10000)
    temperature: float = Field(..., ge=0.0, le=3.0)
    json_format: Optional[bool] = False


# -----      data      -----
class BatchData(BaseModel):
    id: int
    name: str
    status: str
    prompt: str
    progress: Optional[str] = None
    endpoint: str
    file_reader: str
    model: str
    # todo: delay
    temperature: float
    costs_in_usd: float
    created_at: datetime
    updated_at: datetime
    started_at: Optional[datetime]
    stopped_at: Optional[datetime]


class BatchTaskData(BaseModel):
    id: int
    batch_id: int
    file_id: int
    status: str
    prompt_marker: Optional[str]
    output: Optional[str]
    input_token_count: Optional[int]
    output_token_count: Optional[int]
    costs_in_usd: Optional[float]
    created_at: datetime
    updated_at: datetime


class BatchFileData(BaseModel):
    id: int
    batch_id: int
    file_id: int
    name: str
    status: str
    input_token_count: Optional[int]
    output_token_count: Optional[int]
    costs_in_usd: Optional[float]
    batch_tasks: list[BatchTaskData]
    created_at: datetime
    updated_at: datetime
