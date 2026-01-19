from io import BytesIO, StringIO
from typing import Union, Tuple
from ai_tomator.manager.database import Database
from ai_tomator.core.exporter.exporter import BatchExporter


class ExportService:
    def __init__(self, db: Database):
        self.db = db

    def export_batch(self, batch_id: int, mode: str) -> Tuple[Union[StringIO, BytesIO], str, str]:
        return self.export_batches([batch_id], mode)

    def export_batches(self, batch_ids: list[int], mode: str) -> Tuple[Union[StringIO, BytesIO], str, str]:
        results = []
        for batch_id in batch_ids:
            results.extend(self.db.results.list_by_batch(batch_id))
        exporter = BatchExporter(mode)
        return exporter.export(results)
