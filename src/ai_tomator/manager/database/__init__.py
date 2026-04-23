from .base import get_session
from ai_tomator.manager.database.models.user import User as User
from ai_tomator.manager.database.models.group import Group as Group
from ai_tomator.manager.database.ops.endpoint_ops import EndpointOps
from ai_tomator.manager.database.ops.batch_ops import BatchOps
from ai_tomator.manager.database.ops.file_ops import FileOps
from ai_tomator.manager.database.ops.prompt_ops import PromptOps
from ai_tomator.manager.database.ops.user_ops import UserOps
from ai_tomator.manager.database.ops.group_ops import GroupOps
from ai_tomator.manager.database.ops.worker_ops import WorkerOps
from ai_tomator.manager.database.ops.export_ops import ExportOps


class Database:
    batches: BatchOps
    endpoints: EndpointOps
    files: FileOps
    prompts: PromptOps
    users: UserOps
    groups: GroupOps
    workers: WorkerOps
    export: ExportOps

    def __init__(self, db_path):
        self.SessionLocal = get_session(str(db_path))
        self.batches = BatchOps(self.SessionLocal)
        self.endpoints = EndpointOps(self.SessionLocal)
        self.files = FileOps(self.SessionLocal)
        self.prompts = PromptOps(self.SessionLocal)
        self.users = UserOps(self.SessionLocal)
        self.groups = GroupOps(self.SessionLocal)
        self.worker = WorkerOps(self.SessionLocal)
        self.export = ExportOps(self.SessionLocal)
