from fastapi import Request, status, HTTPException
from repository import UserRepository
from api.v1.schemas import AuthCredential, RefreshToken
from database.models import User
from helpers import verify_password, create_access_token, create_refresh_token, verify_token
from config.config import config
from typing import Optional
from uuid import UUID


class AuthenticationService:

    def __init__(self, user_repo:UserRepository):
        self.user_repo = user_repo
    
    async def authenticate_user(self, request:Request, payload:AuthCredential):
        
        payload:dict = payload.model_dump()
        username:str = payload.get("username")
        unhashed_password:str = payload.get("password")

        user:Optional[User] = await self.user_repo.check_username(username)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Invalid username or password."
            )
        
        is_authenticated:bool = verify_password(user.password, unhashed_password)
        if not is_authenticated:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Invalid username or password."
            )
        update_user_payload:dict = {
            "is_authenticated":True
        }

        try:
            await self.user_repo.update_user(user, user.tenant_id, update_user_payload)
        except Exception as error:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(error)
            )
        import asyncio
        await asyncio.sleep(10)
        
        jwt_payload:dict = {
            "user_id":str(user.user_id),
            "username":user.username,
            "user_firstname":user.first_name,
            "user_lastname":user.last_name,
            "user_role_id":str(user.role_id),
            "user_tenant_id":str(user.tenant_id),
            "email":user.email
        }
        access_token:str = create_access_token(jwt_payload, config.jwt_algo, config.jwt_secret_key, config.access_token_expire_minutes)
        refresh_token:str = create_refresh_token(jwt_payload, config.jwt_algo, config.jwt_secret_key, config.refresh_token_expire_minutes)
        
        return {
            "access_token":access_token,
            "refresh_token":refresh_token,
            "token_type":'Bearer',
            "tenant_id":user.tenant_id,
            "user_id":user.user_id,
            "role":user.role_id
        }
    
    async def verify_refresh_token(self, payload:RefreshToken):
        
        payload:dict = payload.model_dump()
        refresh_token:str = payload.get("refresh_token")

        try:
            data:dict = verify_token(refresh_token, config.jwt_algo, config.jwt_secret_key)
        except Exception as error:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail = str(error) if error else "Could not validate credentials."
            )
        if  'token_type' not in data or data.get("token_type") != 'refresh':
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid refresh token."
            )
        username:str = data.get("username")
        if not username:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="could not validate credentaisl."
            )
        
        user = await self.user_repo.check_username(username)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found."
            )
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Inactive user."
            )
        
        jwt_payload:dict = {
            "user_id":str(user.user_id),
            "username":user.username,
            "user_firstname":user.first_name,
            "user_lastname":user.last_name,
            "user_role_id":str(user.role_id),
            # "user_role_name":user.role.name,
            "user_tenant_id":str(user.tenant_id),
            "email":user.email
        }
        access_token:str = create_access_token(jwt_payload, config.jwt_algo, config.jwt_secret_key, config.access_token_expire_minutes)
        refresh_token:str = create_refresh_token(jwt_payload, config.jwt_algo, config.jwt_secret_key, config.refresh_token_expire_minutes)

        return {
            "access_token":access_token,
            "refresh_token":refresh_token,
            "token_type":'Bearer',
            "tenant_id":user.tenant_id,
            "user_id":user.user_id,
            "role":user.role_id
        }
        





                