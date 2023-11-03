import celery

from app import config
from app.download_utils import (
    combine_audio_video,
    download_audio_from_piped,
    download_piped_video,
)
from app.helper_classes import Status

settings = config.Settings()

redis_version = "redis" if settings.redis_tls == 0 else "rediss"

celery_broker = f"{redis_version}://{settings.celery_broker_user}{':' if settings.celery_broker_password != '' else ''}{settings.celery_broker_password}{'@' if settings.celery_broker_password != '' else ''}{settings.celery_broker_host}:{settings.celery_broker_port}/{settings.celery_broker_db}"
celery_backend = f"{redis_version}://{settings.celery_backend_user}{':' if settings.celery_backend_password != '' else ''}{settings.celery_backend_password}{'@' if settings.celery_backend_password != '' else ''}{settings.celery_backend_host}:{settings.celery_backend_port}/{settings.celery_backend_db}"

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
async def download_piped_audio_task(self, payload: dict):
    try:
        audio_path, title = download_audio_from_piped(payload["video_id"])
    except Exception as e:
        if self.request.retries == settings.celery_retry_max:
            raise self.retry(exc=SubtaskException(str(e)))

    return {"status": Status.OK}
