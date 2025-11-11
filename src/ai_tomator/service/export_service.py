from ai_tomator.core.exporter.exporter import BatchExporter
from ai_tomator.manager.database import Database


class ExportService:
    def __init__(self, db: Database):
        self.db = db

    def export_batch(self, batch_id: int, mode: str) -> str:
        results = self.db.results.list_by_batch(batch_id)
        exporter = BatchExporter(mode)
        return exporter.to_csv(results)
