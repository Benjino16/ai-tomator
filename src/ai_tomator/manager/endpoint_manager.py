from ai_tomator.core.engine.models import EngineHealth
from ai_tomator.core.engine.engine_manager import EngineManager


class EndpointManager:
    def __init__(self, engine_manager: EngineManager):
        self.engine_manager = engine_manager

    def get_models(self, endpoint) -> list[str]:
        return self.engine_manager.endpoint_models(endpoint)

    def get_health(self, endpoint) -> EngineHealth:
        return self.engine_manager.endpoint_health(endpoint)
