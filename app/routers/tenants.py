from fastapi import APIRouter, HTTPException, status, Request, Depends
from schemas.tenants import TenantCreateSchema
from database.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from services import tenant_service
from schemas.responses import BaseResponse


router = APIRouter(prefix="/tenants")

@router.post(
    "/create-tenant",
    status_code=status.HTTP_201_CREATED,
    description="API to create the tenant and user."
)
async def create_tenant(request:Request, payload:TenantCreateSchema, db:AsyncSession=Depends(get_db)):
    await tenant_service.create_tenant(request, payload, db)
    return BaseResponse(
        data=None,
        message="Succesfully created tenant.",
        status=status.HTTP_201_CREATED
    )
