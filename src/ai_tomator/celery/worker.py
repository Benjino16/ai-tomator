from celery import Celery
from ai_tomator.config import ServiceSettings

service_settings = ServiceSettings()

app = Celery(
    "ai_tomator_worker",
    broker=str(service_settings.redis_dsn),
    backend=str(service_settings.redis_dsn),
)

app.conf.beat_schedule = {
    "dispatch-database-tasks": {
        "task": "ai_tomator.celery.tasks.dispatch_database_tasks.dispatch_database_tasks",
        "schedule": 5.0,
    }
}

app.autodiscover_tasks(["ai_tomator.celery.tasks"])
