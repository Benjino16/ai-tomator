from typing import Optional, List
from pydantic import BaseModel


class PriceCalculationRequest(BaseModel):
    provider: str
    model: str
    file_reader: str
    file_ids: List[str]
    prompt: Optional[str] = None
    output: Optional[str] = None
