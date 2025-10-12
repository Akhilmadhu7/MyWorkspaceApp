from database.models.tenants import Tenant
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from sqlalchemy import select
from uuid import UUID

class TenantRepository:

    def __init__(self, db:AsyncSession):
        self.db = db

    async def get_tenant_by_tenant_id(self, tenant_id:UUID) -> Tenant|None:
        
        query = select(Tenant).where(
            Tenant.tenant_id == tenant_id,
            Tenant.is_deleted.is_(False)
        )
        result = await self.db.execute(query)
        data = result.scalar_one_or_none()
        if not data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Data not found."
            )
        return data


    async def create_tenant(self, payload:dict) -> Tenant|None:
        tenant = Tenant(**payload)
        self.db.add(tenant)
        await self.db.flush()
        return tenant

