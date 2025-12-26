from fastapi import HTTPException, status, Request
from repository import UserRepository, UserInvitationRepository, TokenRepository
from api.v1.schemas import UserResponseSchema, UserCreateAndVerifyInvitationSchema, UpdateUserSchema
from database.models import User, UserInvitation, Token
from exception.exceptions import NotFoundException, ObjectAlreadyExistsException
from logger.logger import logger
from typing import Optional, List
from uuid import UUID


class UserService:

    def __init__(self, user_repo:UserRepository):
        self.user_repo = user_repo

    async def get_user(self, request:Request, user_id:UUID) -> UserResponseSchema:
        
        tenant_id = request.headers.get("X-Tenant-Id", None)
        user:Optional[User] = await self.user_repo.get_user(tenant_id, user_id)
        if not user:
            logger.error(f"User not found for the user: {user_id} and tenant_id: {tenant_id}.")
            NotFoundException("User not found.") 
        return UserResponseSchema.from_orm(user)
    
    async def get_all_users(self, request:Request, user_filters:dict={}) -> List[UserResponseSchema]:
        
        tenant_id:UUID = request.state.tenant_id
        users:List[User] = await self.user_repo.get_all_users(tenant_id, user_filters)
        return [UserResponseSchema.model_validate(user) for user in users]
    
    async def update_user(self, request:Request, user_id:UUID, payload:UpdateUserSchema) -> UserResponseSchema:
        
        tenant_id:UUID = request.state.tenant_id
        user:Optional[User] = await self.user_repo.get_user(tenant_id, user_id)
        if not user:
            logger.error(f"User not found for the user: {user_id} and tenant_id: {tenant_id}.")
            NotFoundException("User not found.")
        
        user_payload:dict = payload.model_dump(exclude_none=True)
        if user_payload.get("email",None):
            existing_user:Optional[User] = await self.user_repo.get_user_by_email(user_payload["email"], tenant_id)
            if existing_user and existing_user.user_id != user.user_id:
                logger.error(f"Another user exists with email: {user_payload['email']} under the tenant_id: {tenant_id}. So user: {user_id} can't update the email: {user_payload['email']}.")
                raise ObjectAlreadyExistsException("Another user with same email already exists.")
            logger.info(f"Another user doesn't exist with the updating email: {user_payload['email']} for the user: {user_id} under the tenant: {tenant_id}.")

        try:
            user:User = await self.user_repo.update_user(user, tenant_id, user_payload)
            await self.user_repo.db.commit() 
            logger.info(f"Successfully updated user. user_id: {user_id} and tenant_id: {tenant_id}")
            return UserResponseSchema.model_validate(user)
        except Exception as error:
            logger.error(f"Error occurred while updating user: {user_id} and tenatn_id: {tenant_id}.")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(error)
            )
        
    async def soft_delete_user(self, request:Request, user_id:UUID) -> None:
        tenant_id:UUID = request.state.tenant_id
        user:Optional[User] = await self.user_repo.get_user(tenant_id, user_id)
        if not user:
            logger.error(f"User not found for the user: {user_id} and tenant_id: {tenant_id}.")
            NotFoundException("User not found.")
        
        try:
            await self.user_repo.update_user(user, tenant_id, {"is_deleted":True})
            await self.user_repo.db.commit() 
            logger.info(f"Successfully updated user. user_id: {user_id} and tenant_id: {tenant_id}")
            return None
        except Exception as error:
            logger.error(f"Error occurred soft deleting user: {user_id} and tenatn_id: {tenant_id}.")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(error)
            )





        



        