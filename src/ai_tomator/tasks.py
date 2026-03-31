import datetime
import time

import os

from celery import Celery

from ai_tomator.manager.file_manager import FileManager
from ai_tomator.manager.file_storage import MinIOStorage
from ai_tomator.manager.llm_client.client_manager import ClientManager
from celery.utils.log import get_task_logger

from ai_tomator.manager.price_calculator import calculate_price
from ai_tomator.manager.database import Database
from ai_tomator.manager.database.models.batch import BatchFileStatus, BatchStatus


app = Celery(
    'tasks',
    broker='redis://redis:6379/0',
    backend=None
)

logger = get_task_logger(__name__)


DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL must be set in environment variable!")

@app.task
def test_task_db():
    db = Database(DATABASE_URL)
    date = datetime.datetime.now()
    db.prompts.add(
        name=f'test prompt | {date}',
        content='Test Prompt Content',
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
    db = Database(DATABASE_URL)
    file_storage = MinIOStorage()

    file_manager = FileManager(file_storage, db)
    client_manager = ClientManager(file_manager)


    print("Test 12345")
    logger.info("Task gestartet")

    db.batches.add_batch_log(
        batch_id, "Batch with id: {} now running".format(batch_id)
    )
    db.batches.update_status(batch_id=batch_id, status=BatchStatus.RUNNING)
    for file in file_infos:
        if False: #todo: stop logic
            db.batches.update_status(batch_id, BatchStatus.STOPPED)
            return
        try:
            db.batches.add_file_log(
                batch_id,
                file["storage_name"],
                "API Request for file : {}".format(file["storage_name"]),
            )
            result = client_manager.process(
                endpoint=endpoint,
                file_reader=file_reader,
                file_path=file["path"],
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
                storage_name=file["storage_name"],
                status=BatchFileStatus.COMPLETED,
                engine_response=result,
                costs_in_usd=price,
            )
            db.batches.add_batch_log(
                batch_id,
                "Engine successfully responded for file: {}".format(
                    batch_file.storage_name
                ),
                batch_file.id,
            )
            db.batches.add_batch_log(
                batch_id, "Response: {}".format(result.output), batch_file.id
            )
            db.results.save(batch_id, file["storage_name"])
        except Exception as e:
            logger.exception(e)
            batch_file = db.batches.update_batch_file_status(
                batch_id=batch_id,
                storage_name=file["storage_name"],
                status=BatchFileStatus.FAILED,
            )
            db.batches.add_batch_log(
                batch_id,
                "Error while processing file: {}".format(batch_file.storage_name),
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