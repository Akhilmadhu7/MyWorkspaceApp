from repository import UserInvitationRepository, RoleRepository, TokenRepository, UserRepository
from database.models import UserInvitation, Token, User, Role
from uuid import UUID
from api.v1.schemas import (
    UserInvitationRequest,
    VerifyUserInvitationToken,
    UserCreateAndVerifyInvitationSchema,
    UserResponseSchema
)
from fastapi import Request, HTTPException, status
from exception.exceptions import ObjectAlreadyExistsException, NotFoundException, CustomException, TimeOutException
from uuid import UUID
from datetime import datetime, timezone, timedelta
from enums import TokenTypeEnum
from config.config import config
from logger.logger import logger
from src.tasks import send_notification
from helpers import hash_password
from typing import Optional
import secrets


class UserInvitationService:

    def __init__(self, user_invitation_repo:UserInvitationRepository, role_repo:RoleRepository, token_repo:TokenRepository, user_repo:UserRepository):
        self.user_invitation_repo = user_invitation_repo
        self.role_repo = role_repo
        self.token_repo = token_repo
        self.user_repo = user_repo
    
    async def create_user_invitation(self, request:Request, payload:UserInvitationRequest):

        tenant_id:UUID = request.state.tenant_id
        user_id:UUID = request.state.user_id

        user_invitation_payload:dict = payload.model_dump()
        user_invitation_obj:UserInvitation = await self.user_invitation_repo.get_by_email(
            user_invitation_payload['user_invitation_email']
        )
        if user_invitation_obj:
            logger.info(f"user invitation object exists for the email: {user_invitation_obj.user_invitation_email}")
            if user_invitation_obj.is_user_invitation_accepted and user_invitation_obj.is_user_invitation_accepted:
                logger.error(f"User already exists for the user invitation with the email: {user_invitation_obj.user_invitation_email}.")
                raise ObjectAlreadyExistsException(
                    detail="User already exists.",
                    status_code=status.HTTP_400_BAD_REQUEST
                )
            logger.error(f"User has alreay been invited for the user invitation email: {user_invitation_obj.user_invitation_email}.")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User has already been invited."
            )
        
        role:Optional[Role] = await self.role_repo.get_by_role_id(user_invitation_payload['user_invitation_role'])
        if not role:
            logger.error(f"user invitation role not found: {user_invitation_payload['user_invitation_role']}")
            raise NotFoundException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Role doesn't exist."
            )
        
        user_invitation_payload['user_invitation_tenant_id'] = tenant_id
        user_invitation_payload['user_invitation_role'] = role.role_id
        user_invitation_payload['created_by'] = user_id
        user_invitation_payload['updated_by'] = user_id

        invitation_token_expire_in_minutes:int = config.invitation_token_expire_in_minutes
        invitation_token_expires_at:datetime = datetime.now(timezone.utc) + timedelta(minutes=invitation_token_expire_in_minutes)

        try:
            user_invitation_obj:UserInvitation = await self.user_invitation_repo.create(user_invitation_payload)
            token_paylod:dict = {
                "token":secrets.token_urlsafe(120),
                "token_tenant_id":tenant_id,
                "token_type":TokenTypeEnum.INVITATION.name,
                "user_invitation_id":user_invitation_obj.user_invitation_id,
                "expires_at":invitation_token_expires_at

            }
            token:Token = await self.token_repo.create(token_paylod)
            await self.user_invitation_repo.db.commit()
            await self.token_repo.db.commit()
            logger.info(f"Successfully created user invitation: {user_invitation_obj.user_invitation_id} and token: {token.token_id}.")
            send_notification.apply_async(
                kwargs={
                    'reciever_email': user_invitation_obj.user_invitation_email,
                    'subject': "User invitation.",
                    'message': f"Please click on the link to create your account. {config.domain}/user-invitation/{user_invitation_obj.user_invitation_id}/token/{token.token}"
                }
            )
        except Exception as error:
            logger.error(f"Error occured while creating user invitation object. Error: {error}")
            await self.user_invitation_repo.db.rollback()
            await self.token_repo.db.rollback()
            raise CustomException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(error)
            )
        
        return user_invitation_obj
    
    async def verify_user_invitation(self, request:Request, payload:VerifyUserInvitationToken) -> bool:

        payload:dict = payload.model_dump()
        token_str:str = payload.get("user_invitation_token")
        user_invitation_id:str = payload.get("user_invitation_id")

        
        token:Optional[Token] = await self.token_repo.get_by_token(token_str, TokenTypeEnum.INVITATION.value)
        if not token:
            logger.error(f"Token doesn't exist for the user invitation id: {user_invitation_id}.")
            raise NotFoundException("Invalid token.")
       
        current_time_in_utc:datetime = datetime.now(timezone.utc)
        if current_time_in_utc > token.expires_at:
            logger.error(f"Token has been expired for the user invitation: {user_invitation_id}")
            raise TimeOutException("Token has expired.")
        user_invitation_obj:Optional[UserInvitation] = await self.user_invitation_repo.get_by_id(user_invitation_id)
        if not user_invitation_obj:
            logger.error(f"User invitation doesn't exist for the user_invitation_id: {user_invitation_id}.")
            raise NotFoundException("User invitation not found.")
        
        if token.user_invitation_id != user_invitation_obj.user_invitation_id:
            raise CustomException("Invalid token.")
        
        return True
    
    async def create_user_and_verify_invitation_token(self, payload:UserCreateAndVerifyInvitationSchema):
        
        payload:dict = payload.model_dump()
        user_invitation_id:str = payload.get("user_invitation_id")
        user_invitation_token:str = payload.get("user_invitation_token")
        logger.info(f"User otken: {user_invitation_token}")
        token:Optional[Token] = await self.token_repo.get_by_token(user_invitation_token,TokenTypeEnum.INVITATION.value)
        if not token:
            logger.error(f"Token doesn't exist for the user invitation id: {user_invitation_id}")
            raise NotFoundException("Invalid token.")
        
        current_date_in_utc:datetime = datetime.now(timezone.utc)

        if current_date_in_utc > token.expires_at:
            logger.error(f"Token has been expired. Token expired at: {token.expires_at} and current time: {current_date_in_utc}.")
            raise TimeOutException("Token has been expired.")

        user_invitation_obj:Optional[UserInvitation] = await self.user_invitation_repo.get_by_id(user_invitation_id)
        if not user_invitation_obj:
            logger.error(f"User invitation doesn't exist for the user_invitaiton id: {user_invitation_id}.")
            raise NotFoundException("User invitation not found.")
        
        if token.user_invitation_id != user_invitation_obj.user_invitation_id:
            logger.error(f"invalid token: {type(token.user_invitation_id)} and {type(user_invitation_obj.user_invitation_id)}")
            raise CustomException("Invalid token.")
        
        raw_password:str = payload.get("user_password")
        raw_confirmation_password:str = payload.get("user_confirmation_password")
        if raw_password != raw_confirmation_password:
            logger.error("User password confirmation failed.")
            raise CustomException("Password confirmation failed.")
        
        existing_user:Optional[User] = await self.user_repo.get_user_by_email(user_invitation_obj.user_invitation_email, user_invitation_obj.user_invitation_tenant_id)
        if existing_user:
            logger.error(f"An user already existing with email: {existing_user.email}. Raising error becuase of an user exists with requested user invitation id: {user_invitation_id}.")
            raise ObjectAlreadyExistsException("An user already exists with the email.")

        
        user_payload:dict = {
            "first_name":user_invitation_obj.user_invitation_first_name,
            "last_name":user_invitation_obj.user_invitation_last_name,
            "email":user_invitation_obj.user_invitation_email,
            "username":user_invitation_obj.user_invitation_email,
            "image_url":payload.get("imgae_url"),
            "tenant_id":user_invitation_obj.user_invitation_tenant_id,
            "role_id":user_invitation_obj.user_invitation_role,
            "designation":user_invitation_obj.user_invitation_designation,
            "date_of_birth":payload.get("date_of_birth"),
            "password":hash_password(payload.get("user_password")),
        }

        logger.info("Started creating user.")

        try:
            user:User = await self.user_repo.create_user(user_payload)
            logger.info(f"Successfully created user: {user.user_id} and email: {user.email}.")
            await self.token_repo.delete(token)
            logger.info(f"Successfully deleted token for the user: {user.user_id} and invitation_id: {user_invitation_id}.")
            await self.user_invitation_repo.update(user_invitation_obj, {"is_user_invitation_accepted":True})
            logger.info(f"Successfully updated the user invitation object to is_user_invitation_accepted = True for the user: {user.user_id} and invitation id: {user_invitation_id}.")
            await self.user_repo.db.commit()
            return UserResponseSchema.from_orm(user)
        except Exception as error:
            logger.error(f"Error occurred while creating user: {error}.")
            raise CustomException(str(error))


    
    
        



        


        