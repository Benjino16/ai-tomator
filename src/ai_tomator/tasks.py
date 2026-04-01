import datetime
import time


from celery import Celery

from ai_tomator.manager.file_manager import FileManager
from ai_tomator.manager.file_storage import MinIOStorage
from ai_tomator.manager.llm_client.client_manager import ClientManager
from celery.utils.log import get_task_logger

from ai_tomator.manager.price_calculator import calculate_price
from ai_tomator.manager.database import Database
from ai_tomator.manager.database.models.batch import BatchFileStatus, BatchStatus
from ai_tomator.config import ServiceSettings

service_settings = ServiceSettings()

app = Celery("tasks", broker=str(service_settings.redis_dsn), backend=None)

logger = get_task_logger(__name__)


@app.task
def test_task_db():
    db = Database(service_settings.postgres_dsn)
    date = datetime.datetime.now()
    db.prompts.add(
        name=f"test prompt | {date}",
        content="Test Prompt Content",
        user_id=1,
    )


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
    file_storage = MinIOStorage(
        service_settings.minio_endpoint,
        service_settings.minio_access_key,
        service_settings.minio_secret_key,
        service_settings.minio_bucket,
    )

    file_manager = FileManager(file_storage, db)
    client_manager = ClientManager()

    print("Test 12345")
    logger.info("Task gestartet")

    db.batches.add_batch_log(batch_id, "Batch with id: {} now running".format(batch_id))
    db.batches.update_status(batch_id=batch_id, status=BatchStatus.RUNNING)
    for file in file_infos:
        if False:  # todo: stop logic
            db.batches.update_status(batch_id, BatchStatus.STOPPED)
            return
        try:
            db.batches.add_file_log(
                batch_id,
                file["id"],
                "API Request for file : {}".format(file["id"]),
            )

            file_content = file_manager.download_by_path(file["path"])

            result = client_manager.process(
                endpoint=endpoint,
                file_reader=file_reader,
                file=file_content,
                model=model,
                prompt=prompt,
                temperature=temperature,
                json_format=json_format,
            )
            # try calculating costs
            price = None
            if endpoint["provider"].lower() != "self_hosted":
                try:
                    model = result.model.replace("models/", "")
                    price = calculate_price(
                        result.input_tokens,
                        result.output_tokens,
                        endpoint["provider"],
                        model,
                    )
                except Exception as e:
                    logger.error(e)

            db.batches.update_status(
                batch_id=batch_id,
                status=BatchStatus.RUNNING,
                engine_response=result,
            )
            batch_file = db.batches.update_batch_file_status(
                batch_id=batch_id,
                file_id=file["id"],
                status=BatchFileStatus.COMPLETED,
                engine_response=result,
                costs_in_usd=price,
            )
            db.batches.add_batch_log(
                batch_id,
                "Engine successfully responded for file: {}".format(batch_file.id),
                batch_file.id,
            )
            db.batches.add_batch_log(
                batch_id, "Response: {}".format(result.output), batch_file.id
            )
            db.results.save(batch_id, file["id"])
        except Exception as e:
            logger.exception(e)
            batch_file = db.batches.update_batch_file_status(
                batch_id=batch_id,
                file_id=file["id"],
                status=BatchFileStatus.FAILED,
            )
            db.batches.add_batch_log(
                batch_id,
                "Error while processing file: {}".format(batch_file.id),
                batch_file.id,
            )
            db.batches.update_status(batch_id, BatchStatus.FAILED)
            db.batches.add_batch_log(
                batch_id, "Batch with id {} will terminate now!".format(batch_id)
            )
            return

        time.sleep(delay)
    db.batches.add_batch_log(
        batch_id, "Batch with id {} successfully ended!".format(batch_id)
    )
    db.batches.update_status(batch_id, BatchStatus.COMPLETED)
