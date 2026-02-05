from ..manager.database import Database


class PromptService:
    def __init__(self, db: Database):
        self.db = db

    def add(self, name: str, content: str, user_id: int) -> dict:
        return self.db.prompts.add(name=name, content=content, user_id=user_id)

    def list(self) -> list[dict]:
        return self.db.prompts.list()

    def delete(self, prompt_id: int) -> dict:
        return self.db.prompts.delete(prompt_id=prompt_id)
