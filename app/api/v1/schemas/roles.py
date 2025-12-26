from pydantic import BaseModel, ConfigDict
from uuid import UUID

class RoleResponseSchema(BaseModel):

    role_id:UUID
    role_name:str

    model_config = ConfigDict(from_attributes=True)