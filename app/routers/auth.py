from fastapi import APIRouter, Depends, status, HTTPException, Request
from schemas import AuthCredential
from dependancies import get_auth_service
from services import AuthenticationService


router = APIRouter(prefix="/auth")

@router.post(
    "/login",
    description="Api to get login access token."
)
async def login_user(request:Request, payload:AuthCredential,auth_service:AuthenticationService = Depends(get_auth_service)):
    try:
        return await auth_service.authenticate_user(request, payload)
    except HTTPException as error:
        raise HTTPException(
            status_code=error.status_code,
            detail=error.detail
        )
    except Exception as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error)
        )