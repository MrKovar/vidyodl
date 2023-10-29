from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Settings and configuration for the application.

    For sensitive information, use environment variables in .env file.
    """

    # Sets default download path for videos. Recommended to be volume mounted to a folder on the host machine.
    download_path: str = "download"

    # Celery settings
    # If using TLS for Redis, set redis_tls_version to
    redis_tls: int = 0

    # Defaults to celery-redis container from compose file
    celery_broker_host: str = "celery-redis"
    celery_backend_host: str = "celery-redis"

    # Default users for celery-redis container
    celery_broker_user: str = ""
    celery_backend_user: str = ""

    # Default passwords for celery-redis container
    celery_broker_password: str = "pass123"
    celery_backend_password: str = "pass123"

    # Default port for redis
    celery_broker_port: int = 6379
    celery_backend_port: int = 6379

    # Sets redis dbs for celery
    celery_broker_db: int = 0
    celery_backend_db: int = 1

    # Celery retry settings
    celery_retry_max: int = 5
    celery_retry_delay: int = 10

    # Redis token cache settings
    # Sets default parameters for redis token cache (used for Youtube OAuth)
    redis_token_cache_host: str = "redis://celery-redis"
    redis_token_cache_password: str = "pass123"
    redis_token_cache_db: int = 2

    # Use .env file locally to change any settings above
    class Config:
        env_file = ".env"
