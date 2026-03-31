from fastapi import FastAPI
from contextlib import asynccontextmanager
from pathlib import Path
import logging
import os
import secrets
import string

from ai_tomator.api.routes import build_router
from ai_tomator.manager.database import Database
from ai_tomator.manager.endpoint_manager import EndpointManager
from ai_tomator.manager.file_manager import FileManager
from ai_tomator.manager.batch_manager import BatchManager
from ai_tomator.manager.file_storage import MinIOStorage
from ai_tomator.manager.llm_client import ClientManager
from ai_tomator.service.endpoint_service import EndpointService
from ai_tomator.service.export_service import ExportService
from ai_tomator.service.file_service import FileService
from ai_tomator.service.batch_service import BatchService
from ai_tomator.service.jwt_authenticator import JWTAuthenticator
from ai_tomator.service.login_service import LoginService
from ai_tomator.service.price_service import PriceService
from ai_tomator.service.prompt_service import PromptService
from ai_tomator.logger_config import setup_logging
from ai_tomator.service.user_service import UserService

BASE_DIR = Path(__file__).resolve().parent

setup_logging()
logger = logging.getLogger(__name__)

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable not set")

MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT")
MINIO_PORT = os.getenv("MINIO_PORT")
MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY")
MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY")
MINIO_BUCKET = os.getenv("MINIO_BUCKET")

AUTH_REQUIRED = os.getenv("AUTH_REQUIRED", "true").lower() != "false"
if not AUTH_REQUIRED:
    AUTH_REQUIRED = False

def generate_jwt_key(length=32):
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
    return "".join(secrets.choice(alphabet) for _ in range(length))


# configuration for jwt_authenticator
ALGORITHM = "HS256"
JWT_ENCRYPTION_KEY = os.getenv("JWT_ENCRYPTION_KEY")
if not JWT_ENCRYPTION_KEY:
    JWT_ENCRYPTION_KEY = generate_jwt_key()
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440"))
SECURE_COOKIES = os.getenv("SECURE_COOKIES", "true").lower() != "false"
if not SECURE_COOKIES:
    logger.warning("SECURE_COOKIES: {}".format(SECURE_COOKIES))
    logger.warning("This should only be in a save test environment.")



def create_app(required_user_auth=True) -> FastAPI:

    app = FastAPI(title="AI-Tomator")

    @app.get("/health")
    async def health():
        return {"status": "ok"}

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        db = Database(DATABASE_URL)

        file_storage = MinIOStorage(MINIO_ENDPOINT + ":" + MINIO_PORT, MINIO_ACCESS_KEY, MINIO_SECRET_KEY, MINIO_BUCKET)

        file_manager = FileManager(file_storage, db)
        client_manager = ClientManager(file_manager)
        batch_manager = BatchManager(db)
        endpoint_manager = EndpointManager(client_manager)

        jwt_authenticator = JWTAuthenticator(
            JWT_ENCRYPTION_KEY, ALGORITHM, db, required_user_auth, SECURE_COOKIES
        )
        login_service = LoginService(
            db, JWT_ENCRYPTION_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES
        )
        user_service = UserService(db)

        file_service = FileService(db, file_manager)
        endpoint_service = EndpointService(db, endpoint_manager)
        batch_service = BatchService(db, batch_manager, endpoint_service, file_service)
        export_service = ExportService(db)
        prompt_service = PromptService(db)
        price_service = PriceService(db, file_service)

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
            price_service,
        )
        app.include_router(router, prefix="/api")

        if not required_user_auth:
            try:
                login_service.register_user("localhost", "localhost")
            except ValueError:
                logger.warning("Failed to register user: localhost")

        yield

    app.router.lifespan_context = lifespan
    return app


app = create_app(AUTH_REQUIRED)
