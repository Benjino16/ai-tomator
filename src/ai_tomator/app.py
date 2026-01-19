from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
from pathlib import Path
import os

from ai_tomator.api.routes import build_router
from ai_tomator.manager.database import Database
from ai_tomator.manager.endpoint_manager import EndpointManager
from ai_tomator.manager.file_manager import FileManager
from ai_tomator.manager.batch_manager import BatchManager
from ai_tomator.core.engine.engine_manager import EngineManager
from ai_tomator.service.endpoint_service import EndpointService
from ai_tomator.service.export_service import ExportService
from ai_tomator.service.file_service import FileService
from ai_tomator.service.batch_service import BatchService
from ai_tomator.service.jwt_authenticator import JWTAuthenticator
from ai_tomator.service.login_service import LoginService
from ai_tomator.service.prompt_service import PromptService
from ai_tomator.logger_config import setup_logging
from ai_tomator.service.user_service import UserService

BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "webui" / "static"

DB_PATH = os.getenv("DB_PATH", "data/db/database.db")
# ensure db path exists
db_file = Path(DB_PATH).resolve()
db_file.parent.mkdir(parents=True, exist_ok=True)

STORAGE_DIR = str(Path(os.getenv("STORAGE_DIR", "data/storage")).resolve())

# create absolut db path (robust for docker / local / pyinstaller)
DATABASE_URL = f"sqlite:///{Path(DB_PATH).resolve()}"

SECRET_KEY = "change_this"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # One Day


def create_app(db_path, storage_dir) -> FastAPI:
    setup_logging()
    app = FastAPI(title="AI-Tomator")

    @app.get("/health")
    async def health():
        return {"status": "ok"}

    app.mount(
        "/ui",
        StaticFiles(directory=STATIC_DIR, html=True),
        name="webui",
    )

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        db = Database(db_path)
        engine_manager = EngineManager()
        file_manager = FileManager(storage_dir, db)
        batch_manager = BatchManager(db, engine_manager)
        endpoint_manager = EndpointManager(engine_manager)

        jwt_authenticator = JWTAuthenticator(SECRET_KEY, ALGORITHM, db)
        login_service = LoginService(
            db, SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES
        )
        user_service = UserService(db)

        file_service = FileService(db, file_manager)
        endpoint_service = EndpointService(db, endpoint_manager)
        batch_service = BatchService(db, batch_manager, endpoint_service, file_service)
        export_service = ExportService(db)
        prompt_service = PromptService(db)

        file_manager.sync_storage_with_db()
        batch_manager.recover_batches()

        router = build_router(
            file_service,
            batch_service,
            endpoint_service,
            export_service,
            prompt_service,
            login_service,
            jwt_authenticator,
            user_service,
        )
        app.include_router(router, prefix="/api")

        yield

    app.router.lifespan_context = lifespan
    return app


app = create_app(DATABASE_URL, STORAGE_DIR)
