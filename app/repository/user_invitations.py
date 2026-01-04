from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, exists
from uuid import UUID
from database.models import UserInvitation
from typing import List

class UserInvitationRepository:

    def __init__(self, db:AsyncSession):
        self.db = db

    async def create(self, payload:dict) -> UserInvitation:
        user_invitation = UserInvitation(**payload)
        self.db.add(user_invitation)
        await self.db.flush()
        await self.db.refresh(user_invitation)
        return user_invitation

    async def get_by_id(self, user_invitation_id:UUID) -> UserInvitation:
        query = select(UserInvitation).where(
            UserInvitation.user_invitation_id==user_invitation_id
        )
        result = await self.db.execute(query)
        user_invitation = result.scalar_one_or_none()
        return user_invitation

    async def getAll(self, tenant_id:UUID) -> List[UserInvitation]:
        query = select(UserInvitation).where(
            UserInvitation.user_invitation_tenant_id==tenant_id
        )
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def get_by_email(self, user_email:str) -> UserInvitation:
        query = select(UserInvitation).where(
            UserInvitation.user_invitation_email == user_email
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
    
    async def is_user_exists(self, user_email:str) -> bool:
        query = select(
            exists().where(UserInvitation.user_invitation_email==user_email)
        )
        result = await self.db.execute(query)
        return bool(result.scalar())
    
    async def delete(self, user_invitation:"UserInvitation") -> bool:
        await self.db.delete(user_invitation)
        return True
    
    async def update(self, user_invitation:"UserInvitation", payload:dict) -> UserInvitation:
        for key, value in payload.items():
            if hasattr(user_invitation, key):
                setattr(user_invitation, key, value)
        await self.db.flush()
        return user_invitation

