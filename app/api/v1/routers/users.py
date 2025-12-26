from fastapi import Request, status, Depends, APIRouter
from uuid import UUID
from ..schemas import BaseResponse, UserResponseSchema, UpdateUserSchema
from dependancies import get_user_service
from services import UserService
from typing import List

router = APIRouter(prefix="/users")

@router.get(
    "/{user_id}",
    status_code=status.HTTP_200_OK,
    description="Api to get the user details.",
    response_model=BaseResponse[UserResponseSchema]
)
async def get_user_api(request:Request, user_id:UUID, user_service:UserService = Depends(get_user_service)):

    user:UserResponseSchema = await user_service.get_user(request, user_id)
    return BaseResponse(
        data = user,
        message = 'Successfully fetched user details.',
        status=status.HTTP_200_OK
    )

@router.get(
    "/",
    status_code=status.HTTP_200_OK,
    description="Api to fetch all users.",
    response_model=BaseResponse[List[UserResponseSchema]]
)
async def get_all_users(
    request:Request,
    user_service:UserService=Depends(get_user_service)
):
    users:List[UserResponseSchema] = await user_service.get_all_users(request, {})
    return BaseResponse[List[UserResponseSchema]](
        data=users,
        message="Successfully fetched users.",
        status=status.HTTP_200_OK
    )

@router.patch(
    "/{user_id}",
    description="Api to update user.",
    status_code=status.HTTP_200_OK,
    response_model=BaseResponse[UserResponseSchema]
)
async def update_user(
    request:Request,
    user_id:UUID,
    payload:UpdateUserSchema,
    user_service:UserService = Depends(get_user_service)
):
    user:UserResponseSchema = await user_service.update_user(request, user_id, payload)
    return BaseResponse[UserResponseSchema](
        data=user,
        status=status.HTTP_200_OK,
        message="Successfully updated user."
    )

@router.delete(
    "/{user_id}",
    description="Api to update user.",
    status_code=status.HTTP_200_OK,
    response_model=BaseResponse
)
async def delete_user(
    request:Request,
    user_id:UUID,
    user_service:UserService = Depends(get_user_service)
):
    await user_service.soft_delete_user(request, user_id)
    return BaseResponse[UserResponseSchema](
        data=None,
        status=status.HTTP_200_OK,
        message="Successfully deleted user."
    )