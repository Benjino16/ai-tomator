from pydantic import BaseModel


class EndpointData(BaseModel):
    name: str
    engine: str
    url: str | None = None
    token: str | None = None
