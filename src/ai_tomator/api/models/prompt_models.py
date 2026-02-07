from pydantic import BaseModel, Field


class PromptRequest(BaseModel):
    name: str = Field(..., min_length=3, max_length=30)
    content: str = Field(..., min_length=3, max_length=5000)


class PromptData(BaseModel):
    id: int
    name: str
    content: str
