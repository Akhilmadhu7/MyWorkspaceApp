from pydantic import BaseModel, ConfigDict
from uuid import UUID
from datetime import datetime, date
from typing import Optional
from .roles import RoleResponseSchema

class UserResponseSchema(BaseModel):

    user_id:UUID
    first_name:str
    last_name:Optional[str] = None
    email:str
    role:RoleResponseSchema
    date_of_birth:Optional[date] = None
    designation:Optional[str] = None
    image_url:Optional[str] = None
    tenant_id:UUID
    created_at:datetime
    updated_at:datetime

    model_config = ConfigDict(from_attributes=True)


class UpdateUserSchema(BaseModel):

    first_name:Optional[str] = None
    last_name:Optional[str] = None
    email:Optional[str] = None
    role:Optional[UUID] = None
    designation:Optional[str] = None
    image_url:Optional[str] = None


    