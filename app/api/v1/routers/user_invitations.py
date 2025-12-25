from fastapi import APIRouter, HTTPException, status, Depends, Request
from dependancies import get_user_invitation_service
from ..schemas import (
    UserInvitationRequest,
    BaseResponse,
    UserInvitationResponse,
    VerifyUserInvitationToken,
    UserCreateAndVerifyInvitationSchema,
    UserResponseSchema
)
from services import UserInvitationService

router = APIRouter(prefix="/user-invitations")

@router.post("/", response_model=BaseResponse)
async def create_user_invitation(
    request:Request,
    user_invitation_request:UserInvitationRequest,
    user_invitation_service:UserInvitationService = Depends(get_user_invitation_service)
    ) -> BaseResponse:

    user_invitation_response = await user_invitation_service.create_user_invitation(request, user_invitation_request)
    return BaseResponse[UserInvitationResponse](
        data=user_invitation_response,
        message="Invitation has been sent to the user.",
        status=status.HTTP_201_CREATED
    )

@router.post("/verify-invitation", response_model=BaseResponse)
async def verify_user_invitation(
    request:Request,
    user_invitation_token:VerifyUserInvitationToken,
    user_invitation_service:UserInvitationService = Depends(get_user_invitation_service)
) -> BaseResponse:
    response = await user_invitation_service.verify_user_invitation(request, user_invitation_token)
    return BaseResponse[bool](
        data=response,
        message="Succesfully verified.",
        status=status.HTTP_200_OK
    )
    

@router.post("/create-user", response_model=BaseResponse)
async def create_user(
    payload:UserCreateAndVerifyInvitationSchema,
    user_invitation_service:UserInvitationService = Depends(get_user_invitation_service)
) -> BaseResponse:
    user:UserResponseSchema = await user_invitation_service.create_user_and_verify_invitation_token(payload)
    return BaseResponse[UserResponseSchema](
        data = user,
        message="Successfully created user.",
        status=status.HTTP_201_CREATED
    )