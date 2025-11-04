from .base import BaseExportMode
from typing import List, Any, Dict
import pandas as pd
import json


class ExpandedExportMode(BaseExportMode):
    """
    ExpandedExportMode flattens and expands JSON-like output data into a tabular structure.
    It tries to interpret the 'output' field as JSON, expanding lists and dictionaries into
    separate rows or columns for CSV export.
    """

    name = "expanded"

    def to_csv(self, results: List[Dict[str, Any]]) -> str:
        expanded_rows = []

        for row in results:
            base = {k: v for k, v in row.items() if k != "output"}
            try:
                parsed = json.loads(row.get("output", "{}"))
            except json.JSONDecodeError:
                parsed = {"_output_raw": row.get("output", "")}

            if isinstance(parsed, list):
                for item in parsed:
                    new_row = base.copy()
                    if isinstance(item, dict):
                        new_row.update(item)
                    else:
                        new_row["value"] = item
                    expanded_rows.append(new_row)
            elif isinstance(parsed, dict):
                new_row = base.copy()
                new_row.update(parsed)
                expanded_rows.append(new_row)
            else:
                new_row = base.copy()
                new_row["value"] = parsed
                expanded_rows.append(new_row)

        df = pd.DataFrame(expanded_rows)
        return df.to_csv(index=False)
