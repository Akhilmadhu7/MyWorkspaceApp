from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request, HTTPException, status, Response
from helpers import verify_token
from config.config import config
from starlette.responses import JSONResponse
from logger import logger
from uuid import UUID

class JwtVerificationMiddleware(BaseHTTPMiddleware):

    def __init__(self,app):
        super().__init__(app=app)

    async def dispatch(self, request:Request, call_next):
    
        # Immediately return for OPTIONS requests
        if request.method == "OPTIONS":
            return await call_next(request)

        # Exclude `/docs` and `/redoc` endpoints
        if request.url.path.endswith(("/docs","/redoc", "/openapi.json", "/health/", "/login", "create-tenant", "verify-invitation", "create-user")):
            return await call_next(request)
        
        authorization_header:str = request.headers.get("Authorization", None)
        if not authorization_header:
            return JSONResponse(
                status_code=401,
                content={
                    "detail":"Authorization header missing."
                }
            )
        
        token:str = authorization_header.split(" ")[1]
        if not token:
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={
                    "detail":"Bearer token missing."
                }
            )
        
        try:
            logger.info("before verifying jwt token.")
            data:dict = verify_token(token, config.jwt_algo, config.jwt_secret_key)
            
        except Exception as error:
            return JSONResponse(
                status_code=401,
                content={
                    "detail":str(error)
                }
            )
    
        request.state.user_id = UUID(data.get('user_id')) if data.get("user_id") else None
        request.state.tenant_id = UUID(data.get('user_tenant_id')) if data.get("user_tenant_id") else None
        request.state.role_id = UUID(data.get('role_id')) if data.get("role_id") else None
        request.state.username = str(data.get('username')) if data.get("username") else None
        request.state.email = str(data.get('email')) if data.get("email") else None
        request.state.token = token

        logger.info(f"Successfully verified jwt token from: {self.__class__.__name__} and calling next middleware")
        response = await call_next(request)
        logger.info(f"Returning middleware response from: {self.__class__.__name__}")
        return response

        