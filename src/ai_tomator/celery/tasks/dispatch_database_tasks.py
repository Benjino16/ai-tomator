from ai_tomator.celery.worker import app
from ai_tomator.celery.tasks import process_single_file
from celery.utils.log import get_task_logger
from ai_tomator.config import ServiceSettings
from ai_tomator.manager.database import Database
from ai_tomator.manager.database.models.batch import BatchStatus
from ai_tomator.manager.database.models.batch_file import BatchFileStatus
from ai_tomator.manager.database.models.batch_task import BatchTaskStatus

service_settings = ServiceSettings()
logger = get_task_logger(__name__)


@app.task
def dispatch_database_tasks():
    db = Database(service_settings.postgres_dsn)

    for task in db.worker.get_failed_tasks_with_open_retry():
        db.batches.add_batch_task(
            batch_id=task.batch_id,
            file_id=task.file_id,
            batch_file_id=task.batch_file_id,
            prompt=task.prompt,
            prompt_marker=task.prompt_marker,
            retry_task_id=task.id,
        )

    for batch_file in db.worker.get_running_batch_files_with_no_pending_task():
        db.batches.update_batch_file_status(batch_file.id, BatchFileStatus.COMPLETED)

    for batch in db.worker.get_running_batches_with_no_pending_task():
        db.batches.update_status(batch.id, BatchStatus.COMPLETED)

    scheduled_batches = db.worker.get_batches_with_status(BatchStatus.SCHEDULED)
    logger.info(f"Fetched {len(scheduled_batches)} scheduled batches")
    for batch in scheduled_batches:
        # todo: check if scheduled date is passed and then queue the batch
        pass

    queued_batches = db.worker.get_batches_with_status(BatchStatus.QUEUED)
    logger.info(f"Fetched {len(queued_batches)} queued batches")
    for batch in queued_batches:
        if not batch.queue_batch or not db.worker.check_for_running_batch_on_endpoint(
            batch.endpoint_id
        ):
            db.batches.update_status(batch.id, BatchStatus.RUNNING)
        else:
            logger.info(
                f"Batch {batch.id} can not start yet, the worker is still occupied by another batch!"
            )

    running_batches = db.worker.get_batches_with_status(BatchStatus.RUNNING)
    logger.info(f"Fetched {len(running_batches)} running batches")
    for batch in running_batches:

        if db.worker.count_failed_task_of_batch(batch.id) > batch.max_retries:
            db.batches.update_status(batch.id, BatchStatus.FAILED)
            # todo: set remaining batch files failed
            # todo: set remaining batch tasks failed

        if db.worker.count_running_tasks_on_batch(batch.id) >= batch.max_parallel_tasks:
            continue
        if (
            db.worker.count_started_in_last_minute_tasks_on_batch(batch.id)
            >= batch.max_tasks_per_minute
        ):
            continue

        task = db.worker.get_queued_task_from_batch_id(batch.id)
        if task:
            endpoint = db.worker.get_endpoint(batch.endpoint_id)
            file_path = db.worker.get_file_path(task.file_id)
            worker_task = process_single_file.delay(
                batch_id=batch.id,
                batch_task={
                    "id": task.id,
                    "file_id": task.file_id,
                    "batch_file_id": task.batch_file_id,
                    "path": file_path,
                    "prompt": task.prompt,
                    "marker": task.prompt_marker,
                },
                endpoint=endpoint,
                file_reader=batch.file_reader,
                model=batch.model,
                prompt=task.prompt,
                temperature=batch.temperature,
                json_format=batch.json_format,
            )
            db.batches.update_batch_task_status(
                task.id, BatchTaskStatus.RUNNING, worker_task_id=worker_task.id
            )
            db.batches.update_batch_file_status(  # todo: set to queued when no tasks running
                task.batch_file_id, BatchFileStatus.RUNNING
            )
