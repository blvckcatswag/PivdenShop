import redis

from backend.app.config import Config


def get_redis():
    if Config.REDIS_ENABLED:
        return redis.from_url(Config.REDIS_URL)
    return None


def acquire_lock(r, lock_name, timeout=5):
    return r.set(lock_name, 1, nx=True, ex=timeout)


def release_lock(r, lock_name):
    r.delete(lock_name)
