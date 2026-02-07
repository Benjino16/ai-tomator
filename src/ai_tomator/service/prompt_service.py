from ..manager.database import Database


class PromptService:
    def __init__(self, db: Database):
        self.db = db

    def add(self, name: str, content: str, user_id: int) -> dict:
        return self.db.prompts.add(name=name, content=content, user_id=user_id)

    def list(self, user_id: int) -> list[dict]:
        return self.db.prompts.list(user_id)

    def delete(self, prompt_id: int, user_id: int) -> dict:
        return self.db.prompts.delete(prompt_id=prompt_id, user_id=user_id)
