import redis
from config.config import config




class RedisCache:

    _instance = None

    def __init__(self, host:str, port:str, username:str=None, password:str=None, db:str = 0, **kwargs):
        self.host = host
        self.password = password
        self.username = username
        self.port = port
        self.db = db
        self.kwargs = kwargs
        

    def __new__(cls,*args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def connect(self)-> None:
        try:
            self.redis = redis.Redis(self.host, self.port, self.db, self.username, self.password, **self.kwargs)
            self.redis.ping()
        except redis.AuthenticationError as e:
            raise e
        except redis.ConnectionError as e:
            raise e
        except Exception as e:
            raise e
    
    def get_redis_instance(self) -> redis.Redis:
        return self.redis
    
    def close(self):
        return redis.Redis.close()



redis_cache_manager_instance:RedisCache = RedisCache(config.redis_host, config.redis_port)



    

    



