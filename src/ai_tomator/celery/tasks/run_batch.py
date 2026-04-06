from ai_tomator.celery.worker import app
from ai_tomator.celery.tasks import process_single_file
from celery import group, chord
from celery.utils.log import get_task_logger
from ai_tomator.config import ServiceSettings
from ai_tomator.manager.database import Database
from ai_tomator.manager.database.models.batch import BatchStatus

service_settings = ServiceSettings()
logger = get_task_logger(__name__)


@app.task
def run_batch(
    batch_id,
    file_infos,
    endpoint,
    file_reader,
    model,
    prompt,
    delay,
    temperature,
    json_format,
):
    db = Database(service_settings.postgres_dsn)
    db.batches.update_status(batch_id=batch_id, status=BatchStatus.RUNNING)

    tasks = group(
        *[
            process_single_file.s(
                batch_id,
                file,
                endpoint,
                file_reader,
                model,
                prompt,
                temperature,
                json_format,
            )
            for file in file_infos
        ]
    )

    # callback after completing all sub-task
    callback = finalize_batch.si(batch_id)
    chord(tasks, callback).apply_async()

@app.task
def finalize_batch(batch_id):
    db = Database(service_settings.postgres_dsn)
    db.batches.update_status(batch_id, BatchStatus.COMPLETED)
    db.batches.add_batch_log(batch_id, f"Batch {batch_id} finalized")