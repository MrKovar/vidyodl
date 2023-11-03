from redis.asyncio import Redis, from_url

from app import config

settings = config.Settings()


async def connect_token_redis() -> Redis:
    redis = await from_url(
        settings.redis_token_cache_host,
        password=settings.redis_token_cache_password,
        encoding="utf-8",
        db=settings.redis_token_cache_db,
        decode_responses=True,
    )

    return redis


async def get_token_redis():
    redis = await connect_token_redis()
    try:
        yield redis
    finally:
        await redis.close()


async def connect_auth_redis() -> Redis:
    redis = await from_url(
        settings.redis_auth_cache_host,
        password=settings.redis_auth_cache_password,
        encoding="utf-8",
        db=settings.redis_auth_cache_db,
        decode_responses=True,
    )

    return redis


async def get_auth_redis():
    redis = await connect_auth_redis()
    try:
        yield redis
    finally:
        await redis.close()
