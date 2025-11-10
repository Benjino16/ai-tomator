from .base import BaseExportMode
from .raw_mode import RawExportMode
from .expanded_mode import ExpandedExportMode
from typing import List, Any, Dict, Type


class BatchExporter:
    _modes: Dict[str, Type[BaseExportMode]] = {}

    @classmethod
    def register_mode(cls, mode_cls: Type[BaseExportMode]):
        cls._modes[mode_cls.name] = mode_cls

    def __init__(self, mode: str = "raw"):
        if mode not in self._modes:
            raise ValueError(f"Unknown export mode: {mode}")
        self.mode = self._modes[mode]()

    def to_csv(self, results: List[Dict[str, Any]]) -> str:
        return self.mode.to_csv(results)


BatchExporter.register_mode(RawExportMode)
BatchExporter.register_mode(ExpandedExportMode)
