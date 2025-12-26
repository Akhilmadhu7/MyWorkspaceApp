import redis
from config.config import config

import logging
logger = logging.getLogger(__name__)


class RedisCache(redis.Redis):

    _instance = None

    def __init__(self, host:str, port:str, username:str=None, password:str=None, db:str = 0, **kwargs):
        self.redis = redis.Redis(host=host, port=port, password=password,username=username, db=db, **kwargs)
        

    def __new__(cls,*args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def connect(self)-> None:
        try:
            self.redis.ping()
            logger.info("Successfully connected to redis.")
        except redis.AuthenticationError as e:
            logger.error(f"Authentication error while connecting to redis: {e}")
            raise e
        except redis.ConnectionError as e:
            logger.error(f"Connection error while connecting to redis: {e}")
            raise e
        except Exception as e:
            logger.error(f"An exception occurred while connecting to redis: {e}")
            raise e
    
    def get_redis_instance(self) -> redis.Redis:
        return self.redis
    
    def close(self):
        return self.redis.close()



redis_cache_manager_instance:RedisCache = RedisCache(config.redis_host, config.redis_port)
def get_redis():
    return redis_cache_manager_instance.get_redis_instance()


    

    



