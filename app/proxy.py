from typing import Optional


class Proxy:
    def __init__(self, proxy_dict):
        self.name: str = proxy_dict["name"]
        self.url: str = proxy_dict["url"]
        self.up: Optional[bool] = None
        self.speed: Optional[float] = None

    def __str__(self) -> str:
        return f"Proxy <{self.url} | up:{self.up} | speed: {self.speed}>"

    def update(self, proxy):
        self.name = proxy.name
        self.url = proxy.url
        self.up = proxy.up
        self.speed = proxy.speed
