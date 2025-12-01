from io import StringIO
from fastapi import Query
from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from ai_tomator.service.export_service import ExportService


def build_export_router(export_service: ExportService):
    router = APIRouter(prefix="/export", tags=["Export"])

    @router.get("/batches")
    def export_csv(mode: str, batch_ids: list[int] = Query()):
        csv_str = export_service.export_batches(batch_ids, mode)
        buffer = StringIO(csv_str)
        return StreamingResponse(
            buffer,
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=results.csv"},
        )

    return router
