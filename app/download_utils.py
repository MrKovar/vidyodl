import ffmpeg
from pytube import Playlist

from app import config
from app.helper_classes import Status
from app.Piped import Piped

settings = config.Settings()

path = settings.download_path


def get_youtube_video_list_from_playlist(playlist_id: str) -> list:
    playlist = Playlist(f"https://www.youtube.com/playlist?list={playlist_id}")

    return playlist.videos


def download_piped_video(video_id: str) -> dict:
    try:
        download_response = download_av_from_piped(video_id)
        return {
            "status": Status.OK,
            "audio_path": download_response["audio_path"],
            "video_path": download_response["video_path"],
            "title": download_response["title"],
        }
    except Exception as e:
        return {"status": Status.ERROR, "error": str(e)}


def download_youtube_playlist(playlist_id: str, path: str) -> None:
    playlist = Playlist(f"https://www.youtube.com/playlist?list={playlist_id}")

    for video in playlist.videos:
        download_result = download_piped_video(video.video_id, path)
        audio_path, video_path, video_title = (
            download_result["audio_path"],
            download_result["video_path"],
            download_result["title"],
        )
        combine_audio_video(audio_path, video_path, video_title, path)


def combine_audio_video(
    audio_path: str,
    video_path: str,
    title: str,
    format_out: str = "mp4",
    vcodec_out: str = "copy",
    acodec_out: str = "copy",
) -> dict:
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
        ).overwrite_output().run()
    except Exception as e:
        return {"status": Status.ERROR, "error": str(e)}
    return {"status": Status.OK, "info": f"{path}/{title}.{format_out}"}


def download_av_from_piped(video_id: str) -> dict:
    piped_obj = Piped(video_id)

    audio_stream = piped_obj.get_best_audio_stream()
    video_stream = piped_obj.get_best_video_stream()

    audio_path = piped_obj.download_audio_stream(audio_stream)
    video_path = piped_obj.download_video_stream(video_stream)

    return {"audio_path": audio_path, "video_path": video_path, "title": piped_obj.title}


def download_video_from_piped(video_id: str) -> dict:
    piped_obj = Piped(video_id)

    video_stream = piped_obj.get_best_video_stream()

    video_path = piped_obj.download_video_stream(video_stream)

    return {"video_path": video_path, "title": piped_obj.title}


def download_audio_from_piped(video_id: str) -> dict:
    piped_obj = Piped(video_id)

    audio_stream = piped_obj.get_best_audio_stream()

    audio_path = piped_obj.download_audio_stream(audio_stream)

    return {"audio_path": audio_path, "title": piped_obj.title}
