from fastapi import HTTPException, status, Request
from repository import UserRepository
from schemas import UserResponseSchema
from uuid import UUID


class UserService:

    def __init__(self, user_repo:UserRepository):
        self.user_repo = user_repo

    async def get_user(self, request:Request, user_id:UUID):
        
        tenant_id = request.headers.get("X-Tenant-Id", None)
        if not tenant_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Tenant Id required in headers."
            )
        user = await self.user_repo.get_user(tenant_id, user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found."
            )
               
        return UserResponseSchema.from_orm(user)


        