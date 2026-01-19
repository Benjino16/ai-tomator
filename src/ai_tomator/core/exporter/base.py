from typing import List, Dict, Any, Iterable


class BaseExportMode:
    """Common class for all export modes."""

    base_name: str
    modes: Iterable[str]
    default_mode: str

    def export(self, results: List[Dict[str, Any]], mode: str) -> str:
        raise NotImplementedError
