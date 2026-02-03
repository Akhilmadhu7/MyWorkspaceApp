from fastapi import FastAPI, status
from utils.custom_open_api import custom_openapi
from fastapi.middleware.cors import CORSMiddleware
from database.database import db_manager
from api import router, chat_routers
from config.config import config
import contextlib
from cache.cache import redis_cache_manager_instance
from middleware import TenantVerificationMiddleware, JwtVerificationMiddleware, RateLimiterMiddleware
from logger import logger
from alembic import command
from alembic.config import Config
from exception.global_exception_handler import global_exception_handlers
from clients import create_api_client, close_api_client
from websocket_manager import create_websocket_manager, delete_websocket_manager
from typing import Any
import sys
from websocket_manager import WebSocketConnectionManager
from rate_limiter import get_rate_limiter, RateLimiter

@contextlib.asynccontextmanager
async def life_span(app:FastAPI):
    logger.info("Application starting up")
    try:
        await db_manager.connect_to_db()
        logger.info("Successfully connected to databse.")
    except Exception as error:
        logger.error(f"Failed to connect with database. Error occured is: {error}")
        sys.exit(1)
    await redis_cache_manager_instance.connect()
    logger.info("Successfully connected to redis.")
    create_api_client()
    websocket:WebSocketConnectionManager = await create_websocket_manager()
    await websocket.start_listener()
    rate_limiter:RateLimiter = await get_rate_limiter()
    app.state.rate_limiter = rate_limiter
    yield
    logger.info("Applicatin shut down started.")
    await db_manager.clean_up_engines()
    await redis_cache_manager_instance.close()
    await close_api_client()
    delete_websocket_manager()
    logger.info("completed shutdown.")

app = FastAPI(
    title='Boiler plate',
    root_path=f'/api/{config.app_name.lower()}',
    lifespan=life_span
)

app.openapi = lambda:custom_openapi(app)
# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

app.add_middleware(RateLimiterMiddleware)
app.add_middleware(JwtVerificationMiddleware)
# app.add_middleware(TenantVerificationMiddleware)


app.include_router(router)
# app.include_router(chat_routers)
global_exception_handlers(app=app)
