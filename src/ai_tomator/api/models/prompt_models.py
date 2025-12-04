from pydantic import BaseModel


class PromptRequest(BaseModel):
    name: str
    prompt: str


class PromptData(BaseModel):
    id: int
    name: str
    prompt: str
