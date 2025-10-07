from database.models.roles import Role
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException, status
from uuid import UUID


class RoleRepository:


    async def get_owner_role(self, db:AsyncSession) -> Role:
        query = select(Role).where(Role.role_name=='Owner')
        result = await db.execute(query)
        data = result.scalar_one_or_none()
        if not data:
            raise ValueError("should create a new owner role.")
        return data

    @classmethod
    async def get_owner_by_role_id(db:AsyncSession, role_id:UUID) -> Role:
        query = select(Role).where(Role.role_id == role_id)
        result = await db.execute(query)
        data = result.scalar_one_or_none()
        if not data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Role not found."
            )
        return data


role_repository:RoleRepository = RoleRepository()