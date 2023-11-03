import requests

from app.config import Settings
from app.Stream import Stream, download_stream

settings = Settings()


class Piped:
    def __init__(self, video_id):
        self.video_id = video_id
        self.base_url = "https://pipedapi.kavin.rocks"
        self.stream_url = f"{self.base_url}/streams/"

    @property
    def video_properties(self):
        return self.get_video_properties()

    @property
    def audio_streams(self):
        return self.get_video_properties()["audioStreams"]

    @property
    def video_streams(self):
        return self.get_video_properties()["videoStreams"]

    @property
    def title(self):
        return self.get_video_properties()["title"]

    @property
    def description(self):
        return self.get_video_properties()["description"]

    def get_video_properties(self):
        response = requests.get(f"{self.stream_url}{self.video_id}")
        return response.json()

    def get_best_audio_stream(self):
        return Stream(self.audio_streams[0])

    def get_best_video_stream(self):
        return Stream(self.video_streams[0])

    # TODO: Add support for start/stop times
    def download_video_stream(self, stream):
        stream.url = f"{settings.piped_proxy}.{stream.url[23:]}"
        # starting = None
        # ending = None
        return download_stream(stream=stream, title=self.title, file_type="video")

    # TODO: Add support for start/stop times
    def download_audio_stream(self, stream):
        stream.url = f"{settings.piped_proxy}.{stream.url[23:]}"
        # starting = None
        # ending = None
        return download_stream(stream=stream, title=self.title, file_type="audio")
