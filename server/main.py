from fastapi import FastAPI, HTTPException

from app import config, download_utils, models
from app.download_utils import (
    download_audio_from_piped,
    download_av_from_piped,
    get_youtube_video_list_from_playlist,
)
from app.helper_classes import Status
from app.proxy_functions import (
    FASTEST_PROXY,
    UP_PROXIES,
    get_proxies_from_file,
    set_fastest_proxy,
    set_proxies_async,
)
from app.tasks import download_piped_audio_task, download_piped_video_task

description = """
Host your own video downloading API using Piped!
"""

settings = config.Settings()

app_kwargs = dict(title="vidyodl", description=description, version=settings.app_version)

vidyodl_app = FastAPI(**app_kwargs)

# TODO: Add retry for non-celery downloads
# TODO: Change Config to ConfigDict (Pydantic)


@vidyodl_app.get("/health")
async def health_check():
    return {"status": Status.OK, "app": "vidyodl", "version": settings.app_version}


@vidyodl_app.post("/set-proxies")
async def get_proxies():
    try:
        proxy_list = get_proxies_from_file()
        await set_proxies_async(proxy_list)
        set_fastest_proxy()
        return {"status": Status.OK, "proxies": UP_PROXIES}
    except Exception as e:
        return {"status": Status.ERROR, "error": str(e)}


@vidyodl_app.get("/list-proxies")
async def list_proxies():
    return {
        "status": Status.OK,
        "up_proxies": UP_PROXIES,
        "fastest_proxy": FASTEST_PROXY.url,
    }


@vidyodl_app.post("/download", response_model=models.downloadResponseModel)
async def download_from_video_id(video_id: str, use_celery: bool = True) -> models.downloadResponseModel:
    """
    Downloads a video from Piped.

    It

    - **video_id**: The ID of the video to download.
    - **use_celery**: Whether to use Celery or not. (default: True)

    Returns a dict with a the status of the call mapped to 'status' and a mapping of 'info' to either list of task IDs if using Celery
    or a string with the download path if not using Celery.

    If an error occurs, 'status' will map to error, and instead of 'info' there will be an 'error' key mapping to the error message.

    It is recommneded to use Celery for downloading long videos, as it allows for asynchronous downloading.
    Otherwise the API will block until the playlist is downloaded.
    """
    if use_celery:
        try:
            celery_download_task = download_piped_video_task.delay({"video_id": video_id})
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error caught while downloading video: {str(e)}")
        return {"response": {"status": Status.OK, "info": celery_download_task.id}}
    else:
        try:
            download_result = download_av_from_piped(video_id)
            download_utils.combine_audio_video(
                download_result["audio_path"], download_result["video_path"], download_result["title"]
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error caught while downloading video: {str(e)}")
        return {"response": {"status": Status.OK, "info": settings.download_path}}


@vidyodl_app.post("/download-audio", response_model=models.downloadResponseModel)
async def download_audio_from_video_id(video_id: str, use_celery: bool = True) -> models.downloadResponseModel:
    """
    Downloads the audio stream of a video from Piped.

    - **video_id**: The ID of the video to download.
    - **use_celery**: Whether to use Celery or not. (default: True)

    Returns a dict with a the status of the call mapped to 'status' and a mapping of 'info' to either list of task IDs if using Celery
    or a string with the download path if not using Celery.

    If an error occurs, 'status' will map to error, and instead of 'info' there will be an 'error' key mapping to the error message.

    It is recommneded to use Celery for downloading long videos, as it allows for asynchronous downloading.
    Otherwise the API will block until the playlist is downloaded.
    """
    if use_celery:
        try:
            payload = {"video_id": video_id}
            celery_download_task = download_piped_audio_task.delay(payload)
        except Exception as e:
            return {"response": {"status": Status.ERROR, "error": str(e)}}
        return {"response": {"status": Status.OK, "info": celery_download_task.id}}
    else:
        try:
            audio_path, title = download_audio_from_piped(video_id)
        except Exception as e:
            return {"response": {"status": Status.ERROR, "error": str(e)}}
        return {"response": {"status": Status.OK, "info": f"{audio_path}"}}


@vidyodl_app.post("/download-playlist", response_model=models.downloadResponseModel)
async def download_from_playlist_id(playlist_id: str, use_celery: bool = True) -> models.downloadResponseModel:
    """
    Downloads a YouTube playlist from Piped.

    - **playlist_id**: The ID of the playlist to download.
    - **use_celery**: Whether to use Celery or not. (default: True)

    Returns a dict with a the status of the call mapped to 'status' and a mapping of 'info' to either list of task IDs if using Celery
    or a string with the download path if not using Celery.

    If an error occurs, 'status' will map to error, and instead of 'info' there will be an 'error' key mapping to the error message.

    It is recommneded to use Celery for downloading playlists, as it allows for asynchronous downloading.
    Otherwise the API will block until the playlist is downloaded.
    """
    task_list = []

    if use_celery:
        try:
            for youtube_obj in get_youtube_video_list_from_playlist(playlist_id):
                celery_download_task = download_piped_video_task.delay({"video_id": youtube_obj.video_id})
                task_list.append(celery_download_task.id)
        except Exception as e:
            return {"response": {"status": Status.ERROR, "error": str(e)}}

        return {"response": {"status": Status.OK, "info": task_list}}

    else:
        try:
            download_utils.download_youtube_playlist(playlist_id)
        except Exception as e:
            return {"response": {"status": Status.ERROR, "error": str(e)}}

        return {"response": {"status": Status.OK, "info": f"{settings.download_path}"}}
