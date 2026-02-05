from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.responses import FileResponse, Response

from ai_tomator.service.file_service import FileService
from ai_tomator.api.models.file_models import FileData
from fastapi import UploadFile, File, Form
from typing import Optional, List
import os

from ai_tomator.service.jwt_authenticator import JWTAuthenticator


def build_file_router(file_service: FileService, jwt_authenticator: JWTAuthenticator):
    router = APIRouter(prefix="/files", tags=["Files"])

    @router.post("/upload", response_model=FileData)
    def upload_file(
        file: UploadFile = File(...),
        tags: Optional[List[str]] = Form(None),
        user=Depends(jwt_authenticator),
    ):
        return FileData(**file_service.upload_file(file, tags, user["id"]))

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

    @router.get("/tags", response_model=list[str])
    def get_file_tags():
        files = file_service.list_files()

        tags = set()
        for f in files:
            if f.get("tags"):
                tags.update(f["tags"])

        return sorted(tags)

    @router.get("/by-tag/{tag}", response_model=list[FileData])
    def get_files_by_tag(tag: str):
        files = file_service.list_files()

        return [FileData(**f) for f in files if f.get("tags") and tag in f["tags"]]

    return router
