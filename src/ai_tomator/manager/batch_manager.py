from ai_tomator.core.engine.engine_manager import EngineManager
from ai_tomator.core.file_reader.reader_manager import FileReaderManager
from .database import Database
import threading
import time
import logging

logger = logging.getLogger(__name__)


class BatchManager:
    def __init__(self, db: Database, mode: str = "local"):
        self.db = db
        self.mode = mode
        self.engine = EngineManager()
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
        self.db.batches.update_status(batch_id=batch_id, status="running")
        for file in file_infos:
            if stop_flag.is_set():
                self.db.batches.update_status(batch_id, "stopped")
                return
            try:
                result = self.engine.process(
                    endpoint=endpoint,
                    file_reader=file_reader,
                    file_path=file["path"],
                    model=model,
                    prompt=prompt,
                    temperature=temperature,
                )
                self.db.batches.update_batch_file_status(
                    batch_id, file["storage_name"], "done"
                )
                self.db.results.save(
                    batch_id, file["storage_name"], input="", output=result
                )
            except Exception as e:
                self.db.batches.update_status(batch_id, "error")
                logger.exception(e)
                return

            time.sleep(delay)
        self.db.batches.update_status(batch_id, "done")

    def stop_batch(self, batch_id):
        if batch_id in self._stop_flags:
            db_batch_entry = self.db.batches.update_status(batch_id, "stopping")
            self._stop_flags[batch_id].set()
            return db_batch_entry
        else:
            raise ValueError(f"Batch {batch_id} not found or not running.")

    def recover_batches(self):
        for status in ("running", "started"):
            for batch in self.db.batches.list(status=status):
                self.db.batches.update_status(batch["id"], "error")

    def get_engines(self):
        return self.engine.get_engines()

    def get_file_readers(self):
        return FileReaderManager.get_supported()
