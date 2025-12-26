from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request, status
from starlette.responses import JSONResponse
from cache.cache import get_redis
from database.database import get_db
from repository import TenantRepository
from logger.logger import logger


class TenantVerificationMiddleware(BaseHTTPMiddleware):

    async def dispatch(self, request, call_next):

        # Exclude `/docs` and `/redoc` endpoints
        if request.url.path.endswith(("/docs", "/redoc", "/openapi.json","/health")):
            return await call_next(request)
        tenant_id = request.headers.get(
            "X-Tenant-Id"
        )  # get tenant id from request headers(required)
        if not tenant_id:
            return JSONResponse(
                status_code=400, content={"detail": "tenant id required."}
            )
  
        request.state.tenant_id = tenant_id

        response = await call_next(request)
        return response
        
