from .endpoint_service import EndpointService
from .file_service import FileService
from ..manager.batch_manager import BatchManager
from ..manager.database import Database
from ..manager.database.models.batch import BatchStatus


class BatchService:
    def __init__(
        self,
        db: Database,
        batch_manager: BatchManager,
        endpoint_service: EndpointService,
        file_service: FileService,
    ):
        self.batch_manager = batch_manager
        self.db = db
        self.endpoint_service = endpoint_service
        self.file_service = file_service

    def start(
        self,
        prompt_id: int,
        files: list[str],
        endpoint_name: str,
        file_reader: str,
        model: str,
        delay: float,
        temperature: float,
        user_id: int,
    ) -> dict:
        batch_name = f"batch_{hash(model + endpoint_name)}"
        endpoint = self.endpoint_service.get(endpoint_name, user_id, True)

        prompt = self.db.prompts.get(prompt_id, user_id)
        if not prompt:
            raise RuntimeError(f"Prompt {prompt_id} not found")

        prompt_content = prompt["content"]
        engine = endpoint["engine"]

        file_infos = []
        for name in files:
            path = self.file_service.get_file_path(name)
            if path is None:
                raise ValueError(f"Invalid file: {name}")
            file_infos.append({"storage_name": name, "path": path})

        db_batch = self.db.batches.add(
            name=batch_name,
            status=BatchStatus.STARTING,
            files=files,
            engine=engine,
            endpoint=endpoint_name,
            file_reader=file_reader,
            prompt=prompt_content,
            model=model,
            temperature=temperature,
            user_id=user_id,
        )
        batch_id = db_batch["id"]
        self.batch_manager.start_batch(
            batch_id,
            file_infos,
            endpoint,
            file_reader,
            model,
            prompt_content,
            delay,
            temperature,
        )
        return db_batch

    def stop(self, batch_id: int, user_id: int) -> dict:
        batch = self.db.batches.get(batch_id, user_id)
        if batch is None:
            raise ValueError(f"Batch {batch_id} does not exist")
        if batch["status"] in (
            BatchStatus.STOPPED,
            BatchStatus.STOPPING,
            BatchStatus.COMPLETED,
            BatchStatus.FAILED,
        ):
            raise RuntimeError(f"Batch {batch_id} already stopped")
        return self.batch_manager.stop_batch(batch_id)

    def get_batch(self, batch_id: int, user_id: int) -> dict:
        return self.db.batches.get(batch_id, user_id)

    def get_batch_files(self, batch_id: int, user_id: int) -> dict:
        return self.db.batches.get_files(batch_id, user_id)

    def get_batch_log(self, batch_id: int, user_id: int) -> dict:
        return self.db.batches.get_log(batch_id, user_id)

    def list_batches(self, user_id: int) -> dict:
        result = self.db.batches.list(user_id)
        return result

    def list_engines(self) -> dict:
        result = self.batch_manager.get_engines()
        return result

    def list_file_readers(self) -> dict:
        result = self.batch_manager.get_file_readers()
        return result
