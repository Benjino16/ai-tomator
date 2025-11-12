from fastapi import APIRouter, HTTPException, status
from ai_tomator.api.models.endpoint_models import EndpointData
from ai_tomator.core.exceptions import NameAlreadyExistsError
from ai_tomator.service.endpoint_service import EndpointService


def build_endpoint_router(endpoint_service: EndpointService):
    router = APIRouter(prefix="/endpoints", tags=["Endpoints"])

    @router.post("/add", response_model=EndpointData)
    def add_endpoint(ep: EndpointData):
        try:
            return endpoint_service.add(ep.name, ep.engine, ep.url, ep.token)
        except NameAlreadyExistsError as e:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))

    @router.get("/", response_model=list[EndpointData])
    def list_endpoints():
        return endpoint_service.list()

    @router.delete("/delete/{name}", response_model=EndpointData)
    def delete_endpoint(name: str):
        return endpoint_service.delete(name)

    return router
