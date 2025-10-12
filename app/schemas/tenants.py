from pydantic import BaseModel, Field, ConfigDict
from uuid import UUID
from datetime import datetime,date
from typing import Optional

class TenantCreateSchema(BaseModel):

    tenant_name:str = Field(..., min_length=3, max_length=100)
    first_name:str = Field(..., max_length=100, min_length=3)
    last_name:Optional[str] = Field(None, max_length=100)
    user_email:str = Field(..., max_length=200)
    designation:Optional[str] = Field(None, max_length=50)
    date_of_birth:Optional[date] = Field(None)




class TenantResponse(BaseModel):

    tenant_id:UUID
    tenant_name:str
    tenant_code:str
    timezone:str
    created_at:datetime
    updated_at:datetime

    model_config = ConfigDict(from_attributes=True)




    