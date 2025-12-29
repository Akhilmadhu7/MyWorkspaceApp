from fastapi import APIRouter
from .health import router as health_router
from .tenants import router as tenant_router
from .users import router as user_router
from .auth import router as auth_router
from .user_invitations import router as user_invitation_router
from .chat import router as chat_routers


router = APIRouter(prefix="/v1")
router.include_router(health_router, tags=['health'])
router.include_router(tenant_router, tags=['tenant'])
router.include_router(user_router, tags=['users'])
router.include_router(auth_router, tags=["auth"])
router.include_router(user_invitation_router, tags=['user-invitations'])

router.include_router(chat_routers)