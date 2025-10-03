from cache.cache import redis_cache_manager_instance
from redis import Redis

def get_redis_client() -> Redis:
    return redis_cache_manager_instance.get_redis_instance()