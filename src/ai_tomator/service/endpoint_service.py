from ..manager.database import Database
from ..manager.endpoint_manager import EndpointManager


class EndpointService:
    def __init__(self, db: Database, endpoint_manager: EndpointManager):
        self.db = db
        self.endpoint_manager = endpoint_manager

    def add(
        self, name: str, engine: str, url: str | None = None, token: str | None = None
    ) -> dict:
        self.db.endpoints.add(name, engine, url, token)
        return {"name": name, "engine": engine, "status": "added"}

    def get(self, name: str, show_api=False) -> dict:
        endpoint = self.db.endpoints.get(name, show_api)
        return endpoint

    def health(self, name) -> bool:
        endpoint = self.db.endpoints.get(name, True)
        health = self.endpoint_manager.get_health(endpoint)
        return health.healthy

    def models(self, name) -> list[str]:
        endpoint = self.db.endpoints.get(name, True)
        return self.endpoint_manager.get_models(endpoint)

    def list(self) -> list[dict]:
        return self.db.endpoints.list()

    def delete(self, name: str) -> dict:
        self.db.endpoints.delete(name)
        return {"name": name, "status": "deleted"}
