from ..manager.database import Database
from ..manager.endpoint_manager import EndpointManager


class EndpointService:
    def __init__(self, db: Database, endpoint_manager: EndpointManager):
        self.db = db
        self.endpoint_manager = endpoint_manager

    def add(
        self,
        name: str,
        engine: str,
        user_id: int,
        url: str | None = None,
        token: str | None = None,
    ) -> dict:
        ep = self.db.endpoints.add(name, engine, user_id, url, token)
        return ep

    def get(self, name: str, user_id: int, show_api=False) -> dict:
        endpoint = self.db.endpoints.get(name, user_id, show_api)
        return endpoint

    def health(self, name, user_id: int) -> bool:
        endpoint = self.db.endpoints.get(name, user_id, show_api=True)
        health = self.endpoint_manager.get_health(endpoint)
        return health.healthy

    def models(self, name, user_id: int) -> list[str]:
        endpoint = self.db.endpoints.get(name, user_id, show_api=True)
        return self.endpoint_manager.get_models(endpoint)

    def list(self, user_id: int) -> list[dict]:
        return self.db.endpoints.list(user_id)

    def delete(self, name: str, user_id: int) -> dict:
        self.db.endpoints.delete(name, user_id)
        return {"name": name, "status": "deleted"}
