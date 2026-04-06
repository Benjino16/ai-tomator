from ai_tomator.celery.worker import app
from celery.utils.log import get_task_logger
from ai_tomator.config import ServiceSettings
from ai_tomator.manager.database import Database
from ai_tomator.manager.database.models.batch import BatchFileStatus, BatchStatus
from ai_tomator.manager.file_storage import MinIOStorage
from ai_tomator.manager.file_manager import FileManager
from ai_tomator.manager.llm_client.client_manager import ClientManager
from ai_tomator.manager.price_calculator import calculate_price

service_settings = ServiceSettings()
logger = get_task_logger(__name__)

@app.task(bind=True)
def process_single_file(
    self,
    batch_id,
    file_info,
    endpoint,
    file_reader,
    model,
    prompt,
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

    try:
        # Verarbeite das File
        db.batches.add_file_log(
            batch_id,
            file_info["id"],
            f"API Request for file: {file_info['id']}",
        )
        file_content = file_manager.download_by_path(file_info["path"])
        result = client_manager.process(
            endpoint=endpoint,
            file_reader=file_reader,
            file=file_content,
            model=model,
            prompt=prompt,
            temperature=temperature,
            json_format=json_format,
        )

        # Kosten berechnen
        price = None
        if endpoint["provider"].lower() != "self_hosted":
            try:
                model_name = result.model.replace("models/", "")
                price = calculate_price(
                    result.input_tokens,
                    result.output_tokens,
                    endpoint["provider"],
                    model_name,
                )
            except Exception as e:
                logger.error(e)

        # Erfolg: Status aktualisieren
        db.batches.update_batch_file_status(
            batch_id=batch_id,
            file_id=file_info["id"],
            status=BatchFileStatus.COMPLETED,
            engine_response=result,
            costs_in_usd=price,
        )
        db.batches.add_batch_log(
            batch_id,
            f"Engine successfully responded for file: {file_info['id']}",
            file_info["id"],
        )
        return {"status": "success", "file_id": file_info["id"]}

    except Exception as e:
        logger.exception(e)
        # Fehler: Status aktualisieren
        db.batches.update_batch_file_status(
            batch_id=batch_id,
            file_id=file_info["id"],
            status=BatchFileStatus.FAILED,
        )
        db.batches.add_batch_log(
            batch_id,
            f"Error while processing file: {file_info['id']}",
            file_info["id"],
        )
        # Gib den Fehler zurück, damit run_batch ihn zählen kann
        return {"status": "failed", "file_id": file_info["id"], "error": str(e)}