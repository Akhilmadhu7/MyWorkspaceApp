from fastapi import APIRouter, Depends, status, HTTPException, Request
from ..schemas import AuthCredential, AuthToken, RefreshToken, BaseResponse
from dependancies import get_auth_service
from services import AuthenticationService


router = APIRouter(prefix="/auth")

@router.post(
    "/login",
    description="Api to get login access token.",
    response_model=BaseResponse
)
async def login_user(request:Request, payload:AuthCredential,auth_service:AuthenticationService = Depends(get_auth_service)):
    data:AuthToken = await auth_service.authenticate_user(request, payload)
    return BaseResponse[AuthToken](
        data=data,
        message="Successfully logged in.",
        status=status.HTTP_200_OK
    )
    
@router.post(
    "/refresh-token",
    description="Api to get the new access token using the refresh token.",
    response_model=BaseResponse
)
async def get_access_token(request:Request, payload:RefreshToken, auth_service:AuthenticationService = Depends(get_auth_service)):
    data:AuthToken = await auth_service.verify_refresh_token(payload)
    return BaseResponse[AuthToken](
        data=data,
        message="Successfully fetched access and refresh token.",
        status=status.HTTP_200_OK
    )

@router.post(
    "/logout",
    description="API to logout user.",
    response_model=BaseResponse
)
async def logout_user(request:Request, auth_service:AuthenticationService=Depends(get_auth_service)):
    data:None = await auth_service
