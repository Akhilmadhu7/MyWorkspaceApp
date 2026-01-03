from config.config import config
from redis.asyncio import Redis, ConnectionPool, AuthenticationError, ConnectionError as RedisConnectionError
from redis.exceptions import AuthenticationError as RedisAuthenticationError
from typing import Optional
import logging
import asyncio


logger = logging.getLogger(__name__)



class AsyncRedisManager(Redis):
    """Singleton Redis with proper inheritance & error handling"""
    
    _instance: Optional['AsyncRedisManager'] = None
    _initialized = False

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, host: str, port: int, password: str, username: Optional[str] = None, 
                 db: int = 0, decode_responses: bool = True, max_connections: int = 20,
                 socket_timeout: int = 10, socket_keepalive: bool = True, 
                 retry_on_timeout: bool = True, **kwargs):
        if not self._initialized:
            super().__init__(
                host=host,
                port=port,
                password=password,
                username=username,
                db=db,
                decode_responses=decode_responses,
                max_connections=max_connections,
                socket_timeout=socket_timeout,
                socket_keepalive=socket_keepalive,
                retry_on_timeout=retry_on_timeout,
                health_check_interval=30,
                **kwargs
            )
            self._initialized = True
            logger.info(f"AsyncRedisManager initialized: {host}:{port}")

    async def connect(self) -> bool:
        """connection with retries & detailed errors"""
        max_retries = 5
        retry_delay = 2
        
        for attempt in range(max_retries):
            try:
                await self.ping()
                logger.info("Redis connected successfully")
                return True
                
            except RedisAuthenticationError as e:
                logger.error(f"Redis authentication failed: {e}")
                raise RedisAuthenticationError(f"Invalid credentials: {e}")
                
            except RedisConnectionError as e:
                logger.warning(f"Redis connection failed (attempt {attempt + 1}/{max_retries}): {e}")
                if attempt < max_retries - 1:
                    await asyncio.sleep(retry_delay * (attempt + 1))
                else:
                    raise RedisConnectionError(f"Failed after {max_retries} attempts: {e}")
                    
            except Exception as e:
                logger.error(f"Unexpected Redis error: {type(e).__name__}: {e}")
                raise

    async def safe_close(self):
        """shutdown"""
        try:
            await self.aclose()
            logger.info("Redis connections closed safely")
        except Exception as e:
            logger.warning(f"Redis close warning: {e}")



# Global singleton instance
redis_cache_manager_instance: AsyncRedisManager = AsyncRedisManager(
    host=config.redis_host,
    port=config.redis_port,
    password=config.redis_password,
    username=config.redis_username,
    db=config.redis_db,
    max_connections=20,
    socket_timeout=10,
    socket_keepalive=True,
    retry_on_timeout=True
)

async def get_redis() -> AsyncRedisManager:
    """Get Redis with auto-connect + health check"""
    if not redis_cache_manager_instance._initialized:
        await redis_cache_manager_instance.connect()
    return redis_cache_manager_instance  # Returns MANAGER (not self.redis)


    

    



