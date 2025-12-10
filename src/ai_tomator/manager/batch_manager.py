from ai_tomator.core.engine.engine_manager import EngineManager
from ai_tomator.core.file_reader.reader_manager import FileReaderManager
from .database import Database
from .database.models.batch import BatchStatus, BatchFileStatus
import threading
import time
import logging

logger = logging.getLogger(__name__)


class BatchManager:
    def __init__(self, db: Database, engine_manger: EngineManager, mode: str = "local"):
        self.db = db
        self.mode = mode
        self.engine = engine_manger
        self.active_batches = {}
        self._stop_flags = {}

    def start_batch(
        self,
        batch_id,
        file_infos,
        endpoint,
        file_reader,
        model,
        prompt,
        delay,
        temperature,
    ):
        self.db.batches.add_batch_log(batch_id, "Starting new batch with id: {}".format(batch_id))
        if self.mode == "local":
            stop_flag = threading.Event()
            self._stop_flags[batch_id] = stop_flag

            thread = threading.Thread(
                target=self._run_batch,
                args=(
                    batch_id,
                    file_infos,
                    endpoint,
                    file_reader,
                    model,
                    prompt,
                    delay,
                    temperature,
                    stop_flag,
                ),
            )
            thread.start()
            self.active_batches[batch_id] = thread
        else:
            # implement worker / redis later
            raise ValueError("mode must be 'local'")

    def _run_batch(
        self,
        batch_id,
        file_infos,
        endpoint,
        file_reader,
        model,
        prompt,
        delay,
        temperature,
        stop_flag,
    ):
        self.db.batches.add_batch_log(batch_id, "Batch with id: {} now running".format(batch_id))
        self.db.batches.update_status(batch_id=batch_id, status=BatchStatus.RUNNING)
        for file in file_infos:
            if stop_flag.is_set():
                self.db.batches.update_status(batch_id, BatchStatus.STOPPED)
                return
            try:
                self.db.batches.add_file_log(batch_id, file["storage_name"], "API Request for file : {}".format(file["storage_name"]))
                result = self.engine.process(
                    endpoint=endpoint,
                    file_reader=file_reader,
                    file_path=file["path"],
                    model=model,
                    prompt=prompt,
                    temperature=temperature,
                )
                batch_file = self.db.batches.update_batch_file_status(
                    batch_id=batch_id,
                    storage_name=file["storage_name"],
                    status=BatchFileStatus.COMPLETED,
                )
                self.db.batches.add_batch_log(batch_id, "Engine successfully responded for file: {}".format(batch_file.storage_name), batch_file.id)
                self.db.batches.add_batch_log(batch_id, "Response: {}".format(result.output), batch_file.id)
                self.db.results.save(
                    batch_id, file["storage_name"], engine_response=result
                )
            except Exception as e:
                batch_file = self.db.batches.update_batch_file_status(
                    batch_id=batch_id,
                    storage_name=file["storage_name"],
                    status=BatchFileStatus.FAILED,
                )
                self.db.batches.add_batch_log(batch_id, "Error while processing file: {}".format(batch_file.storage_name), batch_file.id)
                self.db.batches.update_status(batch_id, BatchStatus.FAILED)
                self.db.batches.add_batch_log(batch_id, "Batch with id {} will terminate now!".format(batch_id))
                logger.exception(e)
                return

            time.sleep(delay)
        self.db.batches.add_batch_log(batch_id, "Batch with id {} successfully ended!".format(batch_id))
        self.db.batches.update_status(batch_id, BatchStatus.COMPLETED)

    def stop_batch(self, batch_id):
        if batch_id in self._stop_flags:
            self.db.batches.add_batch_log(batch_id, "Stopping batch with id: {}".format(batch_id))
            db_batch_entry = self.db.batches.update_status(
                batch_id, BatchStatus.STOPPING
            )
            self._stop_flags[batch_id].set()
            return db_batch_entry
        else:
            raise ValueError(f"Batch {batch_id} not found or not running.")

    def recover_batches(self):
        for status in (BatchStatus.RUNNING, BatchStatus.STARTING, BatchStatus.STOPPING):
            for batch in self.db.batches.list(status=status):
                self.db.batches.update_status(batch["id"], BatchStatus.FAILED)

    def get_engines(self):
        return self.engine.get_engines()

    def get_file_readers(self):
        return FileReaderManager.get_supported()
