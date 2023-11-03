import ffmpeg

from app.config import Settings

settings = Settings()


class Stream:
    def __init__(self, stream_data):
        self.stream_data = stream_data
        self.url = stream_data["url"]
        self.format = stream_data["format"]
        self.quality = stream_data["quality"]
        self.mime_type = stream_data["mimeType"]
        self.codec = stream_data["codec"]
        self.audio_track_id = stream_data["audioTrackId"]
        self.audio_track_name = stream_data["audioTrackName"]
        self.audio_track_locale = stream_data["audioTrackLocale"]
        self.video_only = stream_data["videoOnly"]
        self.itag = stream_data["itag"]
        self.bitrate = stream_data["bitrate"]
        self.init_start = stream_data["initStart"]
        self.init_end = stream_data["initEnd"]
        self.index_start = stream_data["indexStart"]
        self.index_end = stream_data["indexEnd"]
        self.width = stream_data["width"]
        self.height = stream_data["height"]
        self.fps = stream_data["fps"]
        self.content_length = stream_data["contentLength"]


def download_stream(
    stream: Stream,
    title: str,
    file_type: str,
) -> str:
    output_path = f"{settings.download_path}/{file_type}"

    file_name = f"{file_type}_{title}"

    file_path = f"{output_path}/{file_name}.{get_file_ext_from_format(stream.format)}"

    if file_type == "video":
        video_stream = ffmpeg.input(stream.url)
        ffmpeg.output(
            video_stream,
            filename=file_path,
            format=get_file_ext_from_format(stream.format),
            vcodec="copy",
            strict="experimental",
        ).overwrite_output().run()
    elif file_type == "audio":
        audio_stream = ffmpeg.input(stream.url)
        ffmpeg.output(
            audio_stream,
            filename=file_path,
            format=get_file_ext_from_format(stream.format),
            acodec="copy",
            strict="experimental",
        ).overwrite_output().run()

    return file_path


def get_file_ext_from_format(format: str) -> str:
    match format:
        case "M4A":
            return "mp4"
        case "WEBMA_OPUS":
            return "webm"
        case "WEBMA_VORBIS":
            return "webm"
        case "WEBM":
            return "webm"
        case "WEBM_OPUS":
            return "webm"
        case "WEBM_VORBIS":
            return "webm"
        case "MPEG_4":
            return "mp4"
        case _:
            return "mp4"
