from fastapi import APIRouter, HTTPException, status, Request, Depends
from ..schemas import TenantCreateSchema, TenantResponse, BaseResponse
from uuid import UUID
from dependancies import get_tenant_service
from services import TenantService


router = APIRouter(prefix="/tenants")

@router.post(
    "/create-tenant",
    status_code=status.HTTP_201_CREATED,
    description="API to create the tenant and user."
)
async def create_tenant(request:Request, payload:TenantCreateSchema, tenant_service:TenantService=Depends(get_tenant_service)):
    await tenant_service.create_tenant(request, payload)
    return BaseResponse(
        data=None,
        message="Succesfully created tenant.",
        status=status.HTTP_201_CREATED
    )


@router.get(
    "/{tenant_id}",
    status_code=status.HTTP_200_OK,
    description="Api to get tenant details by ID.",
    response_model=TenantResponse
)
async def get_tenant(request:Request, tenant_id:UUID, tenant_service:TenantService=Depends(get_tenant_service)):
    tenant = await tenant_service.get_tenant(request, tenant_id)
    return BaseResponse(
        data=tenant,
        message = 'Successfully fetched tenant.',
        status=status.HTTP_200_OK
    )