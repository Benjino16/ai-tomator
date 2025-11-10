from .base import get_session
from ai_tomator.manager.database.ops.endpoint_ops import EndpointOps
from ai_tomator.manager.database.ops.result_ops import ResultOps
from ai_tomator.manager.database.ops.batch_ops import BatchOps
from ai_tomator.manager.database.ops.file_ops import FileOps


class Database:
    batches: BatchOps
    endpoints: EndpointOps
    results: ResultOps
    files: FileOps

    def __init__(self, db_path="sqlite:///ai_tomator.db"):
        self.SessionLocal = get_session(db_path)
        self.batches = BatchOps(self.SessionLocal)
        self.endpoints = EndpointOps(self.SessionLocal)
        self.results = ResultOps(self.SessionLocal)
        self.files = FileOps(self.SessionLocal)
