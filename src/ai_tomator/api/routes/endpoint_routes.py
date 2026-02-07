from fastapi import APIRouter, HTTPException, status, Depends
from ai_tomator.api.models.endpoint_models import EndpointRequest
from ai_tomator.core.exceptions import NameAlreadyExistsError
from ai_tomator.service.endpoint_service import EndpointService
from ai_tomator.service.jwt_authenticator import JWTAuthenticator


def build_endpoint_router(
    endpoint_service: EndpointService, jwt_authenticator: JWTAuthenticator
):
    router = APIRouter(prefix="/endpoints", tags=["Endpoints"])

    @router.post("/add", response_model=EndpointRequest)
    def add_endpoint(ep: EndpointRequest, user=Depends(jwt_authenticator)):
        try:
            return endpoint_service.add(
                ep.name, ep.engine, user["id"], ep.url, ep.token
            )
        except NameAlreadyExistsError as e:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))

    @router.get("/", response_model=list[EndpointRequest])
    def list_endpoints(user=Depends(jwt_authenticator)):
        return endpoint_service.list(user["id"])

    @router.get("/health/{name}", response_model=bool)
    def get_endpoint_health(name: str, user=Depends(jwt_authenticator)):
        return endpoint_service.health(name, user["id"])

    @router.get("/models/{name}", response_model=list[str])
    def get_endpoint_models(name: str, user=Depends(jwt_authenticator)):
        return endpoint_service.models(name, user["id"])

    @router.delete("/delete/{name}", response_model=EndpointRequest)
    def delete_endpoint(name: str, user=Depends(jwt_authenticator)):
        return endpoint_service.delete(name, user["id"])

    return router
