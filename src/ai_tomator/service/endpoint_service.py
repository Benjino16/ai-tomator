from ..manager.database import Database


class EndpointService:
    def __init__(self, db: Database):
        self.db = db

    def add(
        self, name: str, engine: str, url: str | None = None, token: str | None = None
    ) -> dict:
        self.db.endpoints.add(name, engine, url, token)
        return {"name": name, "engine": engine, "status": "added"}

    def get(self, name: str) -> dict:
        endpoint = self.db.endpoints.get(name)
        return endpoint

    def list(self) -> list[dict]:
        return self.db.endpoints.list()

    def delete(self, name: str) -> dict:
        self.db.endpoints.delete(name)
        return {"name": name, "status": "deleted"}
