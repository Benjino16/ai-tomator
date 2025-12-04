from fastapi import APIRouter
from .file_routes import build_file_router
from .batch_routes import build_batch_router
from .endpoint_routes import build_endpoint_router
from .pipeline_routes import build_pipeline_router
from .export_routes import build_export_router
from .prompt_routes import build_prompt_router


def build_router(file_service, batch_service, endpoint_service, export_service, prompt_service):
    router = APIRouter()
    router.include_router(build_file_router(file_service))
    router.include_router(build_batch_router(batch_service))
    router.include_router(build_endpoint_router(endpoint_service))
    router.include_router(build_pipeline_router(batch_service))
    router.include_router(build_export_router(export_service))
    router.include_router(build_prompt_router(prompt_service))
    return router
