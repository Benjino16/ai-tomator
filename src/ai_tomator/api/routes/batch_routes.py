from fastapi import APIRouter

from ai_tomator.api.models.batch_models import BatchData, BatchRunRequest
from ai_tomator.service.batch_service import BatchService


def build_batch_router(batch_service: BatchService):
    router = APIRouter(prefix="/batches", tags=["Batches"])

    @router.post("/start", response_model=BatchData)
    def start_run(request: BatchRunRequest):
        result = batch_service.start(
            prompt=request.prompt,
            files=request.files,
            endpoint_name=request.endpoint,
            file_reader=request.file_reader,
            model=request.model,
            delay=request.delay,
            temperature=request.temperature,
        )
        return BatchData(**result)

    @router.post("/stop")
    def stop_run(batch_id: str):
        result = batch_service.stop(batch_id)
        return BatchData(**result)

    @router.get("/", response_model=list[BatchData])
    def list_runs():
        return batch_service.list_runs()

    return router
