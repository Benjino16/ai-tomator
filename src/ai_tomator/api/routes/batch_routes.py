from fastapi import APIRouter, HTTPException, status

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
    def stop_run(batch_id: int):
        try:
            result = batch_service.stop(batch_id)
            return BatchData(**result)
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    @router.get("/{batch_id}")
    def get_batch(batch_id: int):
        result = batch_service.get_batch(batch_id)
        return BatchData(**result)

    @router.get("/log/{batch_id}")
    def get_batch_log(batch_id: int):
        result = batch_service.get_batch_log(batch_id)
        return result

    @router.get("/", response_model=list[BatchData])
    def list_runs():
        return batch_service.list_batches()

    return router
