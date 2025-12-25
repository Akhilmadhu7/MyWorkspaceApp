from database.models.roles import Role
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException, status
from uuid import UUID


class RoleRepository:

    def __init__(self, db:AsyncSession):
        self.db = db

    async def get_owner_role(self) -> Role:
        query = select(Role).where(Role.role_name=='Owner')
        result = await self.db.execute(query)
        data = result.scalar_one_or_none()
        if not data:
            raise ValueError("should create a new owner role.")
        return data

    async def get_by_role_id(self, role_id:UUID) -> Role:
        query = select(Role).where(Role.role_id == role_id)
        result = await self.db.execute(query)
        data = result.scalar_one_or_none()
        return data
