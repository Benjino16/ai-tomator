# web/static_router.py
from fastapi import APIRouter, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


def create_frontend_router(static_dir: Path) -> APIRouter:
    router = APIRouter()
    static_dir = Path(static_dir)

    @router.get("/{full_path:path}")
    async def serve_spa(request: Request, full_path: str):
        file_path = static_dir / full_path
        if file_path.is_file():
            return await StaticFiles(directory=static_dir).get_response(
                full_path, request.scope
            )
        return HTMLResponse(content=(static_dir / "index.html").read_text())

    return router
