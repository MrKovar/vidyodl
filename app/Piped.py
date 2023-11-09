from random import choice
from typing import Dict, List, Optional

import httpx

from app.config import Settings
from app.proxy_functions import FASTEST_PROXY, UP_PROXIES
from app.Stream import Stream, download_stream

settings = Settings()


class Piped:
    def __init__(self, video_id: str):
        self.video_id: str = video_id
        self._base_url: Optional[str] = "https://pipedapi.kavin.rocks"
        self.stream_url: str = f"{settings.default_proxy}/streams/"
        self._video_properties: Optional[Dict] = None
        self._audio_streams: Optional[List] = None
        self._video_streams: Optional[List] = None

    @property
    def video_properties(self) -> dict:
        if self._video_properties is not None:
            return self._video_properties

        self._video_properties = dict()

        response = httpx.get(f"{self.stream_url}{self.video_id}?instance={FASTEST_PROXY.url}")

        self._video_properties.update(response.json())

        return self._video_properties

    @property
    def audio_streams(self) -> list:
        if self._audio_streams is not None:
            return self._audio_streams
        elif self._video_properties is not None:
            return self._video_properties["audioStreams"]
        return self.video_properties["audioStreams"]

    @property
    def video_streams(self) -> list:
        if self._video_streams is not None:
            return self._video_streams
        return self.video_properties["videoStreams"]

    @property
    def title(self) -> str:
        if self._video_properties is not None:
            return self._video_properties["title"]
        return self.video_properties["title"]

    @property
    def description(self) -> str:
        if self._video_properties is not None:
            return self._video_properties["description"]
        return self.video_properties["description"]

    def set_base_url(self) -> str:
        if FASTEST_PROXY is not None:
            self._base_url = FASTEST_PROXY.url
        elif UP_PROXIES is not None:
            self._base_url = choice(UP_PROXIES[0]).url
        else:
            self._base_url = settings.default_proxy
        return self._base_url

    def get_best_audio_stream(self) -> Stream:
        if self._audio_streams is not None:
            return Stream(self._audio_streams[0])

        return Stream(self.audio_streams[0])

    def get_best_video_stream(self) -> Stream:
        if self._video_streams is not None:
            return Stream(self._video_streams[0])
        return Stream(self.video_streams[0])

    # TODO: Add support for start/stop times
    def download_audio_stream(self, stream) -> str:
        # starting = None
        # ending = None
        return download_stream(stream=stream, title=self.title, file_type="audio")

    # TODO: Add support for start/stop times
    def download_video_stream(self, stream) -> str:
        # starting = None
        # ending = None
        return download_stream(stream=stream, title=self.title, file_type="video")
