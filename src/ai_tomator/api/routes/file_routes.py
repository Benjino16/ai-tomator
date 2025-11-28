from fastapi import APIRouter, HTTPException, status
from fastapi.responses import StreamingResponse, FileResponse, Response

from ai_tomator.service.export_service import ExportService
from ai_tomator.service.file_service import FileService
from ai_tomator.api.models.file_models import FileData
from fastapi import UploadFile, File, Form
from typing import Optional, List
from io import StringIO
import os


def build_file_router(file_service: FileService, export_service: ExportService):
    router = APIRouter(prefix="/files", tags=["Files"])

    @router.post("/upload", response_model=FileData)
    def upload_file(
        file: UploadFile = File(...), tags: Optional[List[str]] = Form(None)
    ):
        return FileData(**file_service.upload_file(file, tags))

    @router.get("/download/{filename}")
    def download_file(filename: str):
        try:
            file_path = file_service.get_file_path(filename)
        except FileNotFoundError:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="File not found"
            )

        if not os.path.isfile(file_path):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="File not found"
            )

        return FileResponse(
            path=file_path, filename=filename, media_type="application/octet-stream"
        )

    @router.delete("/delete/{filename}")
    def delete_file(filename: str):
        try:
            file_service.delete_file(filename)
            return Response(status_code=status.HTTP_204_NO_CONTENT)
        except FileNotFoundError:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="File not found"
            )

    @router.get("/", response_model=list[FileData])
    def list_files():
        return file_service.list_files()

    @router.get("/export")
    def export_csv(batch_id: int, mode: str):
        csv_str = export_service.export_batch(batch_id, mode)
        buffer = StringIO(csv_str)
        return StreamingResponse(
            buffer,
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=results.csv"},
        )

    return router
