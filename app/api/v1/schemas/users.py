from pydantic import BaseModel, ConfigDict
from uuid import UUID
from datetime import datetime, date
from typing import Optional

class UserResponseSchema(BaseModel):

    user_id:UUID
    first_name:str
    last_name:Optional[str] = None
    email:str
    role_id:UUID
    date_of_birth:Optional[date] = None
    designation:Optional[str] = None
    image_url:Optional[str] = None
    tenant_id:UUID
    created_at:datetime
    updated_at:datetime

    model_config = ConfigDict(from_attributes=True)
    