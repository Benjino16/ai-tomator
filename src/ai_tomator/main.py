from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager

from ai_tomator.api.routes import build_router
from ai_tomator.manager.database import Database
from ai_tomator.manager.file_manager import FileManager
from ai_tomator.manager.batch_manager import BatchManager
from ai_tomator.service.endpoint_service import EndpointService
from ai_tomator.service.export_service import ExportService
from ai_tomator.service.file_service import FileService
from ai_tomator.service.batch_service import BatchService


def create_app(db_path, storage_dir) -> FastAPI:
    app = FastAPI(title="AI-Tomator")

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        db = Database(db_path)
        file_manager = FileManager(storage_dir, db)
        batch_manager = BatchManager(db)

        file_service = FileService(db, file_manager)
        endpoint_service = EndpointService(db)
        batch_service = BatchService(db, batch_manager, endpoint_service, file_service)
        export_service = ExportService(db)

        file_manager.sync_storage_with_db()
        batch_manager.recover_batches()

        router = build_router(
            file_service,
            batch_service,
            endpoint_service,
            export_service,
        )
        app.include_router(router, prefix="/api")

        yield

    app.router.lifespan_context = lifespan
    return app


app = create_app("sqlite:///ai_tomator.db", "storage")

if __name__ == "__main__":
    import uvicorn

    print("SwaggerUI: http://localhost:8000/docs")
    uvicorn.run("ai_tomator.main:app", host="localhost", port=8000, reload=True)
