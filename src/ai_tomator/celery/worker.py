from celery import Celery
from ai_tomator.config import ServiceSettings

service_settings = ServiceSettings()

app = Celery("ai_tomator", broker=str(service_settings.redis_dsn), backend=str(service_settings.redis_dsn))


app.autodiscover_tasks(['ai_tomator.celery.tasks'])