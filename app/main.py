from fastapi import FastAPI, status
from utils.custom_open_api import custom_openapi
from fastapi.middleware.cors import CORSMiddleware
from database.database import db_manager
from api import router
from config.config import config
import contextlib
from cache.cache import redis_cache_manager_instance
from middleware import TenantVerificationMiddleware, JwtVerificationMiddleware
from logger import logger
from alembic import command
from alembic.config import Config
from exception.global_exception_handler import global_exception_handlers
from typing import Any
import sys,os

@contextlib.asynccontextmanager
async def life_span(app:FastAPI):
    print("Application starting up")
    try:
        await db_manager.connect_to_db()
        logger.info("Successfully connected to databse.")
    except Exception as error:
        logger.error(f"Failed to connect with database. Error occured is: {error}")
        sys.exit(1)
    redis_cache_manager_instance.connect()
    logger.info("Successfully connected to redis.")
    yield
    print("cleangin up engines")
    await db_manager.clean_up_engines()
    redis_cache_manager_instance.close()
    print("completed cdb clean up")

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
app.add_middleware(JwtVerificationMiddleware)
# app.add_middleware(TenantVerificationMiddleware)


app.include_router(router)
global_exception_handlers(app=app)