import json
import uuid

from fastapi import Depends, FastAPI, HTTPException
from redis.asyncio import Redis

from app import config, download_utils, models
from app.auth import prompt_for_oauth, save_oauth_token
from app.connections import get_token_redis
from app.download_utils import get_youtube_video_list_from_playlist
from app.helper_classes import Status
from app.tasks import download_youtube_video_task

description = """
Self-host your own video downloading API built on top of pytube.
"""

settings = config.Settings()

app_kwargs = dict(title="vidyodl", description=description, version="0.1.0")

vidyodl_app = FastAPI(**app_kwargs)

oauth_expire_time = 300


@vidyodl_app.get("/health")
async def health_check():
    return {"status": Status.OK, "app": "vidyodl", "version": settings.app_version}


@vidyodl_app.post("/oauth")
async def oauth(
    cache_uuid: str = None, redis: Redis = Depends(get_token_redis)
):
    try:
        if cache_uuid:
            if cache_uuid is not None:
                response_data = await redis.get(cache_uuid)
                response_data = json.loads(response_data)
                expiry = save_oauth_token(response_data)
                return {"response": {"status": Status.OK, "info": f"OAuth token saved. Expires at {expiry}"}}
            else:
                raise HTTPException(status_code=400, detail="No cache UUID provided.")
        else:
            response_data, verification_url, user_code = prompt_for_oauth()
            cache_key = uuid.uuid4().hex
            await redis.set(cache_key, json.dumps(response_data))
            await redis.expire(cache_key, oauth_expire_time)
            return {
                "response": {
                    "status": Status.OK,
                    "info": f"Please go to {verification_url} and enter the code {user_code} to authenticate, then run the same request with the 'finish' parameter set to True and the 'cache_uuid' parameter set to {cache_key}.",
                }
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error caught while getting OAuth token: {str(e)}")


@vidyodl_app.post("/download", response_model=models.downloadResponseModel)
async def download_from_video_id(video_id: str, use_celery: bool = True) -> models.downloadResponseModel:
    """
    Downloads a video from YouTube.

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
            audio_path, video_path, title = download_utils.download_youtube_video(video_id)
            download_utils.combine_audio_video(audio_path, video_path, title)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error caught while downloading video: {str(e)}")
        return {"response": {"status": Status.OK, "info": settings.download_path}}
    else:
        try:
            audio_path, video_path, title = download_utils.download_youtube_video(video_id)
            download_utils.combine_audio_video(audio_path, video_path, title)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error caught while downloading video: {str(e)}")
        return {"response": {"status": Status.OK, "info": settings.download_path}}


@vidyodl_app.post("/download-audio", response_model=models.downloadResponseModel)
async def download_audio_from_video_id(video_id: str, use_celery: bool = True) -> models.downloadResponseModel:
    """
    Downloads the audio stream of a video from YouTube.

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
            celery_download_task = download_youtube_video_task.delay({"video_id": video_id})
        except Exception as e:
            return {"response": {"status": Status.ERROR, "error": str(e)}}
        return {"response": {"status": Status.OK, "info": celery_download_task.id}}
    else:
        try:
            audio_path, title = download_utils.download_youtube_audio(video_id, settings.download_path)
        except Exception as e:
            return {"response": {"status": Status.ERROR, "error": str(e)}}
        return {"response": {"status": Status.OK, "info": audio_path}}


@vidyodl_app.post("/download-playlist", response_model=models.downloadResponseModel)
async def download_from_playlist_id(playlist_id: str, use_celery: bool = True) -> models.downloadResponseModel:
    """
    Downloads a playlist from YouTube.

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
                celery_download_task = download_youtube_video_task.delay({"video_id": youtube_obj.video_id})
                task_list.append(celery_download_task.id)
        except Exception as e:
            return {"response": {"status": Status.ERROR, "error": str(e)}}

        return {"response": {"status": Status.OK, "info": task_list}}

    else:
        try:
            download_utils.download_youtube_playlist(playlist_id, settings.download_path)
        except Exception as e:
            return {"response": {"status": Status.ERROR, "error": str(e)}}

        return {"response": {"status": Status.OK, "info": f"{settings.download_path}"}}
