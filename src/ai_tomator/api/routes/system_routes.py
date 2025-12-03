from fastapi import APIRouter


def build_system_router():
    router = APIRouter(tags=["System"])

    @router.get("/health")
    def health():
        return {"status": "ok"}

    return router
