from typing import List, Dict, Any


class BaseExportMode:
    name: str = "base"

    def to_csv(self, results: List[Dict[str, Any]]) -> str:
        raise NotImplementedError
