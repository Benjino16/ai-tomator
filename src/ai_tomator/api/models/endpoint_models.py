from typing import Optional
from pydantic import BaseModel, Field


class EndpointRequest(BaseModel):
    name: str = Field(..., min_length=3, max_length=30)
    engine: str
    url: Optional[str] = Field(None, min_length=3, max_length=300)
    token: Optional[str] = Field(None, min_length=3, max_length=300)


class EndpointResponse(BaseModel):
    name: str
    engine: str
    url: Optional[str]
    token: Optional[str]
