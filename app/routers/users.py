from fastapi import Request, HTTPException, status, Depends, APIRouter
from uuid import UUID
from schemas import BaseResponse
from dependancies import get_user_service
from services import UserService

router = APIRouter(prefix="/users")

@router.get(
    "/{user_id}",
    status_code=status.HTTP_200_OK,
    description="Api to get the user details."
)
async def get_user_api(request:Request, user_id:UUID, user_service:UserService = Depends(get_user_service)):

    user = await user_service.get_user(request, user_id)
    return BaseResponse(
        data = user,
        message = 'Successfully fetched user details.',
        status=status.HTTP_200_OK
    )