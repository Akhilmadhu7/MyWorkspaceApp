from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from database.models import User
from uuid import UUID

class UserRepository:

    def __init__(self, db:AsyncSession):
        self.db = db
    
    async def create_user(self, payload:dict):
        user = User(**payload)
        self.db.add(user)
        return user
    
    async def get_user(self, tenant_id:UUID, user_id:UUID):
        query = select(User).where(
            User.tenant_id == tenant_id,
            User.user_id == user_id
        )
        result = await self.db.execute(query)
        data = result.scalar_one_or_none()
        return data
    
    async def get_users(self, tenant_id:UUID, user_filters:dict = {}):
        query = select(User).where(
            User.tenant_id == tenant_id
        )
        result = await self.db.execute(query)
        data = result.all()
        return data
    
    async def check_username(self, username:str):
        query = select(User).where(
            User.username == username
        )
        result = await self.db.execute(query)
        data = result.scalar_one_or_none()
        return data
    
    async def update_user(self, user_id:UUID, tenant_id:UUID, payload:dict):
        query = update(User).where(
            User.user_id == user_id,
            User.tenant_id == tenant_id
        ).values(**payload).execution_options(synchronize_session="fetch")
        await self.db.execute(query)
        await self.db.commit()
