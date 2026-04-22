import logging

from .endpoint_service import EndpointService
from .file_service import FileService
from ai_tomator.manager.file_reader.reader_manager import FileReaderManager
from ai_tomator.manager.llm_client import ClientManager
from ai_tomator.manager.prompt_interpreter import interpret_prompt
from ..manager.database import Database
from ..manager.database.models.batch import BatchStatus
from ..manager.prompt_interpreter.prompt_interpreter import MultiPrompt

logger = logging.getLogger(__name__)


class BatchService:
    def __init__(
        self,
        db: Database,
        endpoint_service: EndpointService,
        file_service: FileService,
    ):
        self.db = db
        self.endpoint_service = endpoint_service
        self.file_service = file_service
        self.file_reader = FileReaderManager()
        self.client_manager = ClientManager()

    def start(
        self,
        prompt_id: int,
        endpoint_id: int,
        files: list[int],
        file_reader: str,
        model: str,
        temperature: float,
        json_format: bool,
        user_id: int,
        batch_worker_settings,
    ) -> dict:
        batch_name = f"batch_{hash(model + str(endpoint_id) + str(prompt_id))}"
        endpoint = self.endpoint_service.get(endpoint_id, user_id, True)
        if not endpoint:
            raise ValueError(f"Endpoint ID {endpoint_id} does not exist")

        prompt_record = self.db.prompts.get(prompt_id, user_id)
        if not prompt_record:
            raise RuntimeError(f"Prompt ID {prompt_id} not found")

        prompt_content = prompt_record["content"]
        multi_prompt = prompt_record["multi_prompt"]
        logger.info(f"Multi Prompt: {multi_prompt}")
        if multi_prompt:
            try:
                prompts_list = interpret_prompt(prompt_content)
                logger.info("Batch with Multi-Prompt started")
                logger.info(f"Interpretation as {len(prompts_list)} prompts.")
            except Exception as e:
                logger.exception(e)
                raise ValueError(f"Invalid prompt content: {prompt_content}")
        else:
            prompts_list = [MultiPrompt("-", prompt_content)]

        batch_args = {
            "name": batch_name,
            "status": BatchStatus.QUEUED,
            "endpoint_id": endpoint_id,
            "prompt_id": prompt_id,
            "file_reader": file_reader,
            "model": model,
            "temperature": temperature,
            "json_format": json_format,
            "user_id": user_id,
            "batch_worker_settings": batch_worker_settings,
        }

        db_batch = self.db.batches.add(**batch_args)
        self.db.batches.add_batch_log(
            batch_id=db_batch["id"],
            message=f"Batch is now in queue with settings: \n {batch_args}",
        )

        for file_id in files:
            path = self.file_service.get_file_path(file_id, user_id)
            if path is None:
                raise ValueError(f"Invalid file: {file_id}")

            batch_file = self.db.batches.add_batch_file(
                batch_id=db_batch["id"],
                file_id=file_id,
            )
            for prompt in prompts_list:
                self.db.batches.add_batch_task(
                    batch_id=db_batch["id"],
                    file_id=file_id,
                    batch_file_id=batch_file["id"],
                    prompt=prompt.prompt,
                    prompt_marker=prompt.marker,
                )

        return db_batch

    def stop(self, batch_id: int, user_id: int) -> dict:
        pass

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
        result = self.client_manager.get_engines()
        return result

    def list_file_readers(self) -> dict:
        result = self.file_reader.get_supported()
        return result
