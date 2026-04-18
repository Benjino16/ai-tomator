from ai_tomator.celery.worker import app
from celery.utils.log import get_task_logger
from ai_tomator.config import ServiceSettings
from ai_tomator.manager.database import Database
from celery.result import AsyncResult
from ai_tomator.manager.database.models.batch_task import BatchTaskStatus

service_settings = ServiceSettings()
logger = get_task_logger(__name__)


def is_task_dead(task_id):
    result = AsyncResult(task_id, app=app)
    return result.state in ["SUCCESS", "FAILURE", "REVOKED"]


@app.task
def cleanup_crashed_tasks():
    db = Database(service_settings.postgres_dsn)
    for task in db.worker.get_running_batch_tasks():
        if not task.worker_task_id:
            db.batches.update_batch_task_status(task.id, BatchTaskStatus.FAILED)
            continue

        result = AsyncResult(task.worker_task_id, app=app)

        if result.state == "SUCCESS":
            logger.warning(f"Task {task.id} succeeded in Celery but never updated DB")
            db.batches.update_batch_task_status(task.id, BatchTaskStatus.FAILED)
        elif result.state in ["FAILURE", "REVOKED"]:
            logger.warning(f"Task {task.id} is dead with state {result.state}")
            db.batches.update_batch_task_status(task.id, BatchTaskStatus.FAILED)
