from config.config import config
from cache import AsyncRedisManager, get_redis
from datetime import datetime, timezone
from logger.logger import logger

class RateLimiter:

    TOKEN_KEY_PREFIX:str = "rate_limiter:tokens"
    LAST_PREFILL_KEY_PREFIX:str = "rate_limiter:last_refill"

    def __init__(self, redis_client:AsyncRedisManager):
        self.redis_client = redis_client
        self.rate_limiter_capacity = config.rate_limiter_capacity
        self.rate_limiter_refill_rate = config.rate_limiter_refill_rate
        logger.info(f"Rate limiter initialized successfullu: {self.redis_client}")
    
    async def get_available_capacity(self, client_id:str) -> int:
        token_key:str = self.TOKEN_KEY_PREFIX+client_id
        balance_token:int = int(await self.redis_client.get(token_key))
        return balance_token
    
    def get_capacity(self) -> int:
        return config.rate_limiter_capacity

    async def is_request_allowed(self, client_id:str) -> bool:
        
        token_key:str = self.TOKEN_KEY_PREFIX+client_id
        await self.refill_token(client_id)

        current_token_str:str = await self.redis_client.get(token_key)
        current_tokens:int = int(current_token_str)
        logger.info(f"current tokens in request allowed: {current_tokens}")
        if current_tokens <=0:
            logger.error(f"returing false from is request:")
            return False
        
        decremented:int = await self.redis_client.decrby(token_key)
        logger.info(f"Rte tlimier decremented: {decremented}")
        return decremented >= 0
        
    async def refill_token(self, client_id:str) -> None:
        
        token_key:str = self.TOKEN_KEY_PREFIX+client_id
        last_refill_key:str = self.LAST_PREFILL_KEY_PREFIX+client_id
        
        now:int = int(datetime.now(timezone.utc).timestamp()*1000)
        
        last_refill:str|None = await self.redis_client.get(last_refill_key)
        if last_refill is None:
            logger.info(f"Last refil is None. So setting up the capacity in redis with capacity: {config.rate_limiter_capacity}")
            await self.redis_client.set(
                token_key,
                str(config.rate_limiter_capacity)
            )
            await self.redis_client.set(
                last_refill_key,
                str(now)
            )
            return None
        
        last_refill_time:int = int(last_refill)
        elapsed_time:int = now - last_refill_time
        logger.info(f"Rate limiter token last refilled: {last_refill_time}")
        logger.info(f"Rate liimter token elapsed time: {elapsed_time}")

        if elapsed_time <= 1:
            logger.info(f"Rate limiter refill returning None as elapsed time is: {elapsed_time}.")
            return None
        
        tokens_to_add:int = int((elapsed_time*config.rate_limiter_refill_rate))
        if tokens_to_add <= 0:
            logger.info(f"Rate limiter refill returns None as tokens to add: {tokens_to_add}.")
            return None
        
        current_tokens:int = int(await self.redis_client.get(token_key) or "0")
        new_tokens:int = min(config.rate_limiter_capacity, current_tokens+tokens_to_add)
        logger.info(f"Rate limiter tokens to add: {tokens_to_add} current token: {current_tokens} and new token: {new_tokens} for the client: {client_id}")
        await self.redis_client.set(token_key, str(new_tokens))
        await self.redis_client.set(last_refill_key, str(now))
        return None


async def get_rate_limiter() -> RateLimiter:
    return RateLimiter(await get_redis())


    