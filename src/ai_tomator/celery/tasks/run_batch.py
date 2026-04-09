from ai_tomator.celery.worker import app
from ai_tomator.celery.tasks import process_single_file
from celery import group, chord
from celery.utils.log import get_task_logger
from ai_tomator.config import ServiceSettings
from ai_tomator.manager.database import Database
from ai_tomator.manager.database.models.batch import BatchStatus
from ai_tomator.manager.database.models.batch_file import BatchFileStatus

service_settings = ServiceSettings()
logger = get_task_logger(__name__)


@app.task
def run_batch(
    batch_id,
    batch_tasks,
    endpoint,
    file_reader,
    model,
    delay,
    temperature,
    json_format,
):
    db = Database(service_settings.postgres_dsn)
    db.batches.update_status(batch_id=batch_id, status=BatchStatus.RUNNING)

    from collections import defaultdict

    grouped_tasks = defaultdict(list)
    for task in batch_tasks:
        grouped_tasks[task["batch_file_id"]].append(task)

    file_chords = []

    for batch_file_id, tasks_in_file in grouped_tasks.items():
        # Tasks pro Datei in einen group packen
        g = group(
            *[
                process_single_file.s(
                    batch_id,
                    task,
                    endpoint,
                    file_reader,
                    model,
                    task["prompt"],
                    temperature,
                    json_format,
                )
                for task in tasks_in_file
            ]
        )

        # chord bauen, aber NICHT direkt ausführen
        c = chord(g, finalize_batch_file.si(batch_file_id))
        file_chords.append(c)

    # Outer chord für gesamten Batch
    batch_chord = chord(group(*file_chords), finalize_batch.si(batch_id))
    batch_chord.apply_async()


@app.task
def finalize_batch_file(batch_file_id):
    db = Database(service_settings.postgres_dsn)
    db.batches.update_batch_file_status(batch_file_id, BatchFileStatus.COMPLETED)


@app.task
def finalize_batch(batch_id):
    db = Database(service_settings.postgres_dsn)
    db.batches.update_status(batch_id, BatchStatus.COMPLETED)
    db.batches.add_batch_log(batch_id, f"Batch {batch_id} finalized")
