import celery

from app import config
from app.download_utils import (
    combine_audio_video,
    download_audio_from_piped,
    download_piped_video,
)
from app.helper_classes import Status
from app.proxy_functions import update_fastest_proxy

settings = config.Settings()

redis_version = "redis" if settings.redis_tls == 0 else "rediss"

celery_broker = (
    f"{redis_version}://"
    + f"{settings.celery_broker_user}"
    + f"{':' if settings.celery_broker_password != '' else ''}"
    + f"{settings.celery_broker_password}"
    + f"{'@' if settings.celery_broker_password != '' else ''}"
    + f"{settings.celery_broker_host}:{settings.celery_broker_port}"
    + f"/{settings.celery_broker_db}"
)
celery_backend = (
    f"{redis_version}://"
    + f"{settings.celery_backend_user}"
    + f"{':' if settings.celery_backend_password != '' else ''}"
    + f"{settings.celery_backend_password}"
    + f"{'@' if settings.celery_backend_password != '' else ''}"
    + f"{settings.celery_backend_host}:{settings.celery_backend_port}"
    + f"/{settings.celery_backend_db}"
)

celery_app = celery.Celery(
    "celery-vidyodl",
    include=["app.tasks"],
    broker=celery_broker,
    backend=celery_backend,
    broker_connection_retry_on_startup=True,
)


class SubtaskException(Exception):
    """
    Exception raised when a subtask fails.
    """

    pass


@celery_app.task(
    bind=True,
    autoretry_for=(SubtaskException,),
    default_retry_delay=settings.celery_retry_delay,
    retries=settings.celery_retry_max,
)
def download_piped_video_task(self, payload: dict):
    video_id = payload["video_id"]
    download_result = download_piped_video(video_id)
    if download_result["status"] == Status.ERROR:
        raise self.retry(exc=SubtaskException(download_result["error"]))

    audio_path = download_result["audio_path"]
    video_path = download_result["video_path"]
    title = download_result["title"]

    combine_result = combine_audio_video(audio_path, video_path, title)

    if combine_result["status"] == Status.ERROR:
        raise self.retry(exc=SubtaskException(combine_result["error"]))

    return combine_result


@celery_app.task(
    bind=True,
    autoretry_for=(SubtaskException,),
    default_retry_delay=settings.celery_retry_delay,
    retries=settings.celery_retry_max,
)
def download_piped_audio_task(self, payload: dict) -> dict:
    try:
        video_id = payload["video_id"]
        download_response = download_audio_from_piped(video_id)
    except Exception as e:
        if str(e) == "Expecting value: line 1 column 1 (char 0)":
            print("The proxy may be down. Setting a new proxy...")
            update_fastest_proxy()
        raise self.retry(exc=SubtaskException(str(e)))

    return {"status": Status.OK, "info": download_response["audio_path"]}
