from .base import BaseExportMode
from typing import List, Any, Dict
import pandas as pd
import csv


class RawExportMode(BaseExportMode):
    name = "raw"

    def to_csv(self, results: List[Dict[str, Any]]) -> str:
        df = pd.DataFrame(results)
        df = df.replace({r"[\r\n]+": r"\\n"}, regex=True)
        return df.to_csv(index=False, quoting=csv.QUOTE_ALL)
