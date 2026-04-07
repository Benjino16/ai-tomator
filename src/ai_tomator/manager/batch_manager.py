from ai_tomator.celery.tasks.run_batch import run_batch
from .database import Database
from .database.models.batch import BatchStatus
import logging

logger = logging.getLogger(__name__)


class BatchManager:
    def __init__(self, db: Database):
        self.db = db
        self.active_batches = {}

    def start_batch(
        self,
        batch_id,
        file_infos,
        endpoint,
        file_reader,
        model,
        delay,
        temperature,
        json_format,
    ):
        self.db.batches.add_batch_log(
            batch_id, "Starting new batch with id: {}".format(batch_id)
        )

        task = run_batch.delay(
            batch_id=batch_id,
            file_infos=file_infos,
            endpoint=endpoint,
            file_reader=file_reader,
            model=model,
            delay=delay,
            temperature=temperature,
            json_format=json_format,
        )

        logger.info("Created celery task with id {}".format(task.id))

        self.active_batches[batch_id] = task

    def stop_batch(self, batch_id):  # todo: update to celery
        if batch_id in self.active_batches:
            db_batch_entry = self.db.batches.update_status(
                batch_id, BatchStatus.STOPPING
            )
            return db_batch_entry
        else:
            raise ValueError(f"Batch {batch_id} not found or not running.")

    def recover_batches(self):
        for batch in self.db.batches.get_active_batches():
            self.db.batches.update_status(batch["id"], BatchStatus.FAILED)
