from rate_limiter import RateLimiter
from fastapi import Request, status, FastAPI
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi.responses import JSONResponse
from logger.logger import logger


class RateLimiterMiddleware(BaseHTTPMiddleware):

    def __init__(self, app:FastAPI):
        super().__init__(app)


    def __get_client_ip(self, request:Request) -> str:

        client_addr = request.headers.get("X-Forwarded-For", None)
        if client_addr:
            return client_addr.split(",")[0].strip()
        return request.client.host

    async def dispatch(self, request:Request, call_next):
        
        # Exclude `/docs` and `/redoc` endpoints
        if request.url.path.endswith(("/docs", "/redoc","health", "/openapi.json")):
            return await call_next(request)
        
        rate_limiter:RateLimiter = request.app.state.rate_limiter
        client_ip:str  = self.__get_client_ip(request)
        logger.info(f"Requested client ip: {client_ip}")

        try:
            if not await rate_limiter.is_request_allowed(client_ip):
                logger.error(f"Request not allowed.")
                return JSONResponse(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    content={
                        "detail":"Too many requests from client."
                    },
                    headers={
                        "X-Rate-Limiter-Limit":str(rate_limiter.get_capacity()),
                        "X-Rate-Limit-Remaining":str(await rate_limiter.get_available_capacity(client_ip))
                    }
                )
            response = await call_next(request)
            return response
        except Exception as error:
            logger.error(f"Error occurred: {error}")
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={
                    "detail":str(error)
                }
            )
        
        
        