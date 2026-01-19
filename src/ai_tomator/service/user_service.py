from ..manager.database import Database


class UserService:
    def __init__(self, db: Database):
        self.db = db

    def list(self) -> list[dict]:
        return self.db.users.list()
