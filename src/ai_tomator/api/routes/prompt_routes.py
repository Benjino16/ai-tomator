from fastapi import APIRouter, HTTPException, Depends
from starlette import status

from ai_tomator.api.models.prompt_models import PromptData, PromptRequest
from ai_tomator.core.exceptions import NameAlreadyExistsError
from ai_tomator.service.jwt_authenticator import JWTAuthenticator
from ai_tomator.service.prompt_service import PromptService


def build_prompt_router(
    prompt_service: PromptService, jwt_authenticator: JWTAuthenticator
):
    router = APIRouter(prefix="/prompts", tags=["Prompts"])

    @router.post("/add")
    def add_prompt(prompt: PromptRequest, user=Depends(jwt_authenticator)):
        try:
            return prompt_service.add(
                name=prompt.name, content=prompt.content, user_id=user["id"]
            )
        except NameAlreadyExistsError as e:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))

    @router.get("/", response_model=list[PromptData])
    def list_prompts():
        return prompt_service.list()

    @router.delete("/delete/{prompt_id}")
    def delete_prompt(prompt_id: int):
        try:
            return prompt_service.delete(prompt_id=prompt_id)
        except ValueError as e:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

    return router
