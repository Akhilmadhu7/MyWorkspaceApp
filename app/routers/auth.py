from fastapi import APIRouter, Depends, status, HTTPException, Request
from schemas import AuthCredential, AuthToken, RefreshToken
from dependancies import get_auth_service
from services import AuthenticationService


router = APIRouter(prefix="/auth")

@router.post(
    "/login",
    description="Api to get login access token.",
    response_model=AuthToken
)
async def login_user(request:Request, payload:AuthCredential,auth_service:AuthenticationService = Depends(get_auth_service)):
    return await auth_service.authenticate_user(request, payload)
    
@router.post(
    "/refresh-token",
    description="Api to get the new access token using the refresh token.",
    response_model=AuthToken
)
async def get_access_token(request:Request, payload:RefreshToken, auth_service:AuthenticationService = Depends(get_auth_service)):
    return await auth_service.verify_refresh_token(payload)