import pytest
from unittest.mock import MagicMock, patch
from ai_tomator.service.export_service import ExportService


@pytest.fixture
def mock_db():
    db = MagicMock()
    db.results.list_by_batch = MagicMock(return_value=[{"id": 1, "output": "ok"}])
    return db


@pytest.fixture
def service(mock_db):
    return ExportService(db=mock_db)


def test_export_batch_calls_exporter_and_returns_csv(service, mock_db):
    with patch("ai_tomator.service.export_service.BatchExporter") as MockExporter:
        exporter_instance = MagicMock()
        exporter_instance.export.return_value = "csv_data"
        MockExporter.return_value = exporter_instance

        result = service.export_batch(batch_id=123, mode="csv")

        mock_db.results.list_by_batch.assert_called_once_with(123)
        MockExporter.assert_called_once_with("csv")
        exporter_instance.export.assert_called_once_with([{"id": 1, "output": "ok"}])
        assert result == "csv_data"
