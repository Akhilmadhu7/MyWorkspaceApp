from database.models.tenants import Tenant
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from sqlalchemy import select
from uuid import UUID

class TenantRepository:

    @classmethod
    async def get_tenant_by_tenant_id(cls, tenant_id:UUID, db:AsyncSession) -> Tenant|None:
        
        query = select(Tenant).where(
            Tenant.tenant_id == tenant_id,
            Tenant.is_deleted.is_(False)
        )
        result = await db.execute(query)
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Data not found."
            )
        return result


    async def create_tenant(self, payload:dict, db:AsyncSession) -> Tenant|None:
        tenant = Tenant(**payload)
        db.add(tenant)
        await db.flush()
        return tenant


tenant_repository:TenantRepository = TenantRepository()