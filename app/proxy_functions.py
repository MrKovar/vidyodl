import asyncio
import json

import httpx

from app.config import Settings
from app.proxy import Proxy

settings = Settings()

FASTEST_PROXY = Proxy({"name": "default proxy", "url": settings.default_proxy})
UP_PROXIES = []


def get_proxies_from_file():
    with open("./app/proxy.json", "r") as f:
        proxies = json.load(f)["proxy_list"]
    proxy_list = []
    for proxy in proxies:
        proxy_obj = Proxy(proxy)
        proxy_list.append(proxy_obj)
    return proxy_list


def get_fastest_proxy():
    sorted_proxies = sorted(UP_PROXIES, key=lambda proxy: proxy.speed)
    return sorted_proxies[0]


def set_fastest_proxy():
    global FASTEST_PROXY
    FASTEST_PROXY.update(get_fastest_proxy())


def update_fastest_proxy():
    global UP_PROXIES, FASTEST_PROXY
    UP_PROXIES.remove(FASTEST_PROXY)
    FASTEST_PROXY.update(get_fastest_proxy())


async def get_async_healthcheck(session: httpx.AsyncClient, proxy: Proxy):
    try:
        response = await session.request(method="GET", url=f"{proxy.url}/healthcheck")
        if response.status_code == 200:
            proxy.up = True
            proxy.speed = response.elapsed.total_seconds()
            UP_PROXIES.append(proxy)
        else:
            proxy.up = False
            proxy.speed = None
    except Exception:
        proxy.up = False
        proxy.speed = None


async def set_proxies_async(proxy_list: list):
    UP_PROXIES.clear()

    async with httpx.AsyncClient() as session:
        await asyncio.gather(*[get_async_healthcheck(session, proxy) for proxy in proxy_list])
