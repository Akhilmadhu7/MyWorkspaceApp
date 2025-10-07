from fastapi import APIRouter
from .health import router as health_router
from .tenants import router as tenant_router

router = APIRouter()
router.include_router(health_router, tags=['health'])
router.include_router(tenant_router, tags=['tenant'])