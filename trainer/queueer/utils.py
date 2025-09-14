import os
from redis import Redis
from config import REDIS_URL


def ensure_folder_exists(path: str) -> None:
    try:
        os.makedirs(path)
    except OSError:
        pass


def get_redis():
    return Redis.from_url(REDIS_URL)
