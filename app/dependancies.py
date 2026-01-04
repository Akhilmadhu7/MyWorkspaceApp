from repository import (
    UserRepository,
    TenantRepository,
    RoleRepository,
    UserInvitationRepository,
    TokenRepository,
    MessageRepository
)
from services import (
    AuthenticationService,
    UserService,
    TenantService,
    UserInvitationService,
    ChatService,
)
from fastapi import Depends
from websocket_manager import get_websocket_manager, WebSocketConnectionManager
from sqlalchemy.ext.asyncio import AsyncSession
from database.database import get_db

def get_user_repo(db:AsyncSession = Depends(get_db)) -> UserRepository:
    return UserRepository(db)

def get_tenant_repo(db:AsyncSession = Depends(get_db)) -> TenantRepository:
    return TenantRepository(db)

def get_role_repo(db:AsyncSession = Depends(get_db)) -> RoleRepository:
    return RoleRepository(db)

def get_user_invitation_repo(db:AsyncSession = Depends(get_db)) -> UserInvitationRepository:
    return UserInvitationRepository(db)

def get_token_repo(db:AsyncSession = Depends(get_db)) -> TokenRepository:
    return TokenRepository(db)

def get_message_repo(db:AsyncSession = Depends(get_db)) -> MessageRepository:
    return MessageRepository(db)


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

def get_user_invitation_service(
        user_invitation_repo:UserInvitationRepository = Depends(get_user_invitation_repo),
        role_repo: RoleRepository = Depends(get_role_repo),
        token_repo:TokenRepository = Depends(get_token_repo),
        user_repo:UserRepository = Depends(get_user_repo)
    ) -> UserInvitationService:
    return UserInvitationService(user_invitation_repo, role_repo, token_repo, user_repo)

def get_chat_service(
        message_repo:MessageRepository = Depends(get_message_repo),
        websocket_manager:WebSocketConnectionManager = Depends(get_websocket_manager)
    ) -> ChatService:
    return ChatService(message_repo, websocket_manager)