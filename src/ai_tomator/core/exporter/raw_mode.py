from .base import BaseExportMode
from typing import List, Any, Dict
import pandas as pd


class RawExportMode(BaseExportMode):
    name = "raw"

    def to_csv(self, results: List[Dict[str, Any]]) -> str:
        df = pd.DataFrame(results)
        return df.to_csv(index=False)
