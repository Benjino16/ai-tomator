from pydantic import BaseModel


class PromptRequest(BaseModel):
    name: str
    content: str


class PromptData(BaseModel):
    id: int
    name: str
    content: str
