from repository import UserRepository, TenantRepository, RoleRepository
from services import AuthenticationService, UserService, TenantService
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from database.database import get_db

def get_user_repo(db:AsyncSession = Depends(get_db)) -> UserRepository:
    return UserRepository(db)

def get_tenant_repo(db:AsyncSession = Depends(get_db)) -> TenantRepository:
    return TenantRepository(db)

def get_role_repo(db:AsyncSession = Depends(get_db)) -> RoleRepository:
    return RoleRepository(db)


def get_user_service(user_repo:UserRepository = Depends(get_user_repo)) -> UserService:
    return UserService(user_repo=user_repo)

def get_tenant_service(
        tenant_repo:TenantRepository  = Depends(get_tenant_repo),
        user_repo:UserRepository = Depends(get_user_repo),
        role_repo:RoleRepository = Depends(get_role_repo)
    ) -> TenantService:
    return TenantService(tenant_repo=tenant_repo, user_repo=user_repo, role_repo=role_repo)

def get_auth_service(user_repo:UserRepository = Depends(get_user_repo)) -> AuthenticationService:
    return AuthenticationService(user_repo=user_repo)