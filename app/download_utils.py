import ffmpeg
from pytube import Playlist, YouTube

from app import config
from app.helper_classes import Status

settings = config.Settings()


def get_youtube_video_list_from_playlist(playlist_id: str) -> list:
    playlist = Playlist(f"https://www.youtube.com/playlist?list={playlist_id}")

    return playlist.videos


def download_youtube_video(video_id: str, path: str = None) -> tuple:
    youtube_obj = YouTube(f"https://www.youtube.com/watch?v={video_id}", allow_oauth_cache=True)

    if path is None:
        path = settings.download_path

    audio_path = (
        youtube_obj.streams.filter(only_audio=True)
        .order_by("abr")
        .desc()
        .first()
        .download(output_path=f"{path}/audio/", filename_prefix="audio_")
    )
    video_path = (
        youtube_obj.streams.filter(progressive=False, file_extension="mp4")
        .order_by("resolution")
        .desc()
        .first()
        .download(output_path=f"{path}/video/", filename_prefix="video_")
    )

    return audio_path, video_path, youtube_obj.title


def download_youtube_audio(video_id, path: str = None):
    youtube_obj = YouTube(f"https://www.youtube.com/watch?v={video_id}", allow_oauth_cache=True)

    audio_path = (
        youtube_obj.streams.filter(only_audio=True)
        .order_by("abr")
        .desc()
        .first()
        .download(output_path=f"{path}/completed/", filename_prefix="audio_")
    )

    return audio_path, youtube_obj.title


def download_youtube_playlist(playlist_id, path):
    playlist = Playlist(f"https://www.youtube.com/playlist?list={playlist_id}")

    for video in playlist.videos:
        audio_path, video_path, video_title = download_youtube_video(video.video_id, path)
        combine_audio_video(audio_path, video_path, video_title, path)


def combine_audio_video(
    audio_path, video_path, title, path=None, format_out="mp4", vcodec_out="copy", acodec_out="copy"
):
    if path is None:
        path = settings.download_path

    try:
        audio_input = ffmpeg.input(audio_path)
        video_input = ffmpeg.input(video_path)
        ffmpeg.output(
            audio_input,
            video_input,
            f"{path}/completed/{title}.{format_out}",
            format=format_out,
            vcodec=vcodec_out,
            acodec=acodec_out,
            strict="experimental",
        ).run()
    except Exception as e:
        return {"status": Status.ERROR, "error": str(e)}
    return {"status": Status.OK, "info": f"{path}/{title}.{format_out}"}
