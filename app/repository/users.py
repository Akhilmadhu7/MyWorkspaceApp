from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from database.models import User

class UserRepository:
    

    async def create_user(self, payload:dict, db:AsyncSession):
        user = User(**payload)
        db.add(user)
        return user


user_repository:UserRepository = UserRepository()