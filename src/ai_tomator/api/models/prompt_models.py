from pydantic import BaseModel


class PromptData(BaseModel):
    id: int
    name: str
    prompt: str
