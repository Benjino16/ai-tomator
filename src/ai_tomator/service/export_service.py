from ai_tomator.manager.database import Database
from ai_tomator.core.exporter.exporter import BatchExporter


class ExportService:
    def __init__(self, db: Database):
        self.db = db

    def export_batch(self, batch_id: int, mode: str) -> str:
        return self.export_batches([batch_id], mode)

    def export_batches(self, batch_ids: list[int], mode: str) -> str:
        results = []
        for batch_id in batch_ids:
            results.extend(self.db.results.list_by_batch(batch_id))
        exporter = BatchExporter(mode)
        return exporter.to_csv(results)
