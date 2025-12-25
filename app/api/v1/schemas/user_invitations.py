from pydantic import BaseModel,Field, ConfigDict
from typing import Optional
from uuid import UUID
from datetime import datetime, date


class UserInvitationRequest(BaseModel):

    user_invitation_email:str = Field(min_length=11,max_length=200)
    user_invitation_first_name:str = Field(min_length=2, max_length=100)
    user_invitation_last_name:Optional[str] = Field(default=None, min_length=2, max_length=100)
    user_invitation_role:UUID
    user_invitation_designation:Optional[str] = Field(default=None, min_length=5, max_length=50)

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "user_invitation_email": "john.doe@example.com",
                "user_invitation_first_name": "John",
                "user_invitation_last_name": "Doe",
                "user_invitation_role": "235a262d-a2a3-4ccf-8485-72dd28b80652",
                "user_invitation_designation": "Senior Developer",
            }
        }
    )

class UserInvitationResponse(BaseModel):

    user_invitation_id:UUID
    user_invitation_email:str = Field(min_length=11,max_length=200)
    user_invitation_first_name:str = Field(min_length=2, max_length=100)
    user_invitation_last_name:Optional[str] = Field(default=None, min_length=2, max_length=100)
    user_invitation_role:UUID
    user_invitation_designation:Optional[str] = Field(default=None, min_length=5, max_length=50)
    user_invitation_tenant_id:UUID
    is_user_invitation_accepted:bool = False
    created_by:UUID
    updated_by:UUID
    created_at:datetime
    updated_at:datetime

    model_config = ConfigDict(from_attributes=True)

class VerifyUserInvitationToken(BaseModel):

    user_invitation_id:UUID
    user_invitation_token:str

class UserCreateAndVerifyInvitationSchema(BaseModel):

    date_of_birth:Optional[date] = None
    image_url:Optional[str] = None
    user_invitation_id:UUID
    user_invitation_token:str
    user_password:str
    user_confirmation_password:str
