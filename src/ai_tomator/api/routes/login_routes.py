from fastapi import APIRouter, Response, HTTPException
from ai_tomator.service.login_service import LoginService
from ..models.login_models import LoginRequest


def build_login_router(login_service: LoginService):
    router = APIRouter(prefix="/authentication", tags=["Authentication"])

    @router.post("/login", response_model=dict)
    def login(request: LoginRequest, response: Response):

        if not login_service.verify_password(request.username, request.password):
            raise HTTPException(status_code=401, detail="Invalid credentials")

        token = login_service.create_access_token(request.username)

        response.set_cookie(
            key="access_token", value=token, httponly=True, samesite="lax", secure=True
        )

        return {"success": True}

    @router.post("/register", response_model=dict)
    def register(request: LoginRequest):
        try:
            success = login_service.register_user(request.username, request.password)
            return {"success": success}
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))

    return router
