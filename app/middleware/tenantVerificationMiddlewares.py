from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request, status
from starlette.responses import JSONResponse
from cache.cache import get_redis
from database.database import get_db
from repository import TenantRepository


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

        try:
            print("first")
            cache = get_redis()
            print("cache", cache,type(cache))
            tenant = cache.get(f"tenant:id:{tenant_id}")
            print("tenant from cache", tenant)
            if not tenant:
                print("if not tenant")
                async with get_db(request) as db:
                    print("db",db)
                    tenant = await TenantRepository(db).get_tenant_by_tenant_id(tenant_id)
                if not tenant:
                    return JSONResponse(
                        status_code=status.HTTP_404_NOT_FOUND,
                        content={
                            "detail": "Tenant not found."
                        }
                    )
                cache.set(f"tenant:id:{tenant_id}", tenant)
            request.state.tenant_id = tenant.tenant_id
            request.state.tenant_code = tenant.tenant_code
            request.state.tenant_email = tenant.tenant_email

            response = await call_next(request)
            return response
        except Exception as error:
            print("errrrorrrrrr", error)
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={
                    "detail":{
                        str(error)
                    }
                }
            )
