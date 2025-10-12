from fastapi import Request, status, HTTPException
from repository import UserRepository
from schemas import AuthCredential
from helpers import verify_password, create_access_token, create_refresh_token


class AuthenticationService:

    def __init__(self, user_repo:UserRepository):
        self.user_repo = user_repo
    
    async def authenticate_user(self, request:Request, payload:AuthCredential):
        
        payload:dict = payload.model_dump()
        username:str = payload.get("username")
        unhashed_password:str = payload.get("password")

        user = await self.user_repo.check_username(username)
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
        await self.user_repo.update_user(user.user_id, user.tenant_id, update_user_payload)
        
        jwt_payload:dict = {
            "user_id":str(user.user_id),
            "username":user.username,
            "user_firstname":user.first_name,
            "user_lastname":user.last_name,
            "user_role_id":str(user.role_id),
            # "user_role_name":user.role.name,
            "user_tenant_id":str(user.tenant_id)
        }
        algo:str = "HS256"
        key:str = "a-string-secret-at-least-256-bits-long"
        access_token:str = create_access_token(jwt_payload, algo, key, 5)
        refresh_token:str = create_refresh_token(jwt_payload, algo, key, 8)

        return {
            "access_token":access_token,
            "refresh_token":refresh_token,
            "type":'Bearer'
        }
        
        
        
    
        