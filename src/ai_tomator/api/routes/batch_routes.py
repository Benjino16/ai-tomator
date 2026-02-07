from fastapi import APIRouter, HTTPException, status, Depends

from ai_tomator.api.models.batch_models import BatchData, BatchRunRequest
from ai_tomator.service.jwt_authenticator import JWTAuthenticator
from ai_tomator.service.batch_service import BatchService


def build_batch_router(
    batch_service: BatchService, jwt_authenticator: JWTAuthenticator
):
    router = APIRouter(prefix="/batches", tags=["Batches"])

    @router.post("/start", response_model=BatchData)
    def start_run(request: BatchRunRequest, user=Depends(jwt_authenticator)):

        result = batch_service.start(
            prompt_id=request.prompt_id,
            files=request.files,
            endpoint_name=request.endpoint,
            file_reader=request.file_reader,
            model=request.model,
            delay=request.delay,
            temperature=request.temperature,
            user_id=user["id"],
        )
        return BatchData(**result)

    @router.post("/stop")
    def stop_run(batch_id: int, user=Depends(jwt_authenticator)):
        try:
            result = batch_service.stop(batch_id, user["id"])
            return BatchData(**result)
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    @router.get("/{batch_id}")
    def get_batch(batch_id: int, user=Depends(jwt_authenticator)):
        result = batch_service.get_batch(batch_id, user["id"])
        return BatchData(**result)

    @router.get("/files/{batch_id}")
    def get_batch_files(batch_id: int, user=Depends(jwt_authenticator)):
        result = batch_service.get_batch_files(batch_id, user["id"])
        return result

    @router.get("/log/{batch_id}")
    def get_batch_log(batch_id: int, user=Depends(jwt_authenticator)):
        result = batch_service.get_batch_log(batch_id, user["id"])
        return result

    @router.get("/", response_model=list[BatchData])
    def list_runs(user=Depends(jwt_authenticator)):
        return batch_service.list_batches(user["id"])

    return router
