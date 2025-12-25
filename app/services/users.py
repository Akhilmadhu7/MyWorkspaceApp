from fastapi import HTTPException, status, Request
from repository import UserRepository, UserInvitationRepository, TokenRepository
from api.v1.schemas import UserResponseSchema, UserCreateAndVerifyInvitationSchema
from database.models import User, UserInvitation, Token
from exception.exceptions import NotFoundException, TimeOutException, CustomException
from enums import TokenTypeEnum
from datetime import datetime, timezone
from logger.logger import logger
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
        user:User = await self.user_repo.get_user(tenant_id, user_id)
        if not user:
            logger.error(f"User not found for the user: {user_id} and tenant_id: {tenant_id}.")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found."
            )
               
        return UserResponseSchema.from_orm(user)

        



        