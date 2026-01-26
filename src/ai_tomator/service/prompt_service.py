from ..manager.database import Database


class PromptService:
    def __init__(self, db: Database):
        self.db = db

    def add(self, name: str, content: str) -> dict:
        return self.db.prompts.add(name=name, content=content)

    def list(self) -> list[dict]:
        return self.db.prompts.list()

    def delete(self, prompt_id: int) -> dict:
        return self.db.prompts.delete(prompt_id=prompt_id)
