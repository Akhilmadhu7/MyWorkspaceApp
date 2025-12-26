from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from database.models import User
from sqlalchemy.orm import joinedload, selectinload
from uuid import UUID

class UserRepository:

    def __init__(self, db:AsyncSession):
        self.db = db
    
    async def create_user(self, payload:dict):
        user = User(**payload)
        self.db.add(user)
        await self.db.flush()
        await self.db.refresh(user)
        return user
    
    async def get_user(self, tenant_id:UUID, user_id:UUID) -> User:
        query = select(User) \
        .options(joinedload(User.role)) \
        .where(
            User.tenant_id == tenant_id,
            User.user_id == user_id
        )
        result = await self.db.execute(query)
        data = result.scalar_one_or_none()
        return data

    async def get_user_by_email(self, email:str, tenant_id:UUID) -> User:
        query = select(User).where(
            User.email==email,
            User.tenant_id==tenant_id
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
    
    async def get_all_users(self, tenant_id:UUID, user_filters:dict = {}):
        query = select(User) \
        .options(selectinload(User.role)) \
        .where(
            User.tenant_id == tenant_id
        )
        
        result = await self.db.execute(query)
        data = result.scalars().all()
        return data
    
    async def check_username(self, username:str) -> User:
        query = select(User).where(
            User.username == username
        )
        result = await self.db.execute(query)
        data = result.scalar_one_or_none()
        return data
    
    async def update_user(self, user:"User", tenant_id:UUID, payload:dict):
        # query = update(User).where(
        #     User.user_id == user_id,
        #     User.tenant_id == tenant_id
        # ).values(**payload).execution_options(synchronize_session="fetch")
        # await self.db.execute(query)
        # await self.db.commit()
        # await self.db.refresh(user)

        for key, value in payload.items():
            if hasattr(user, key):
                setattr(user, key, value)
        await self.db.flush()
        return user
