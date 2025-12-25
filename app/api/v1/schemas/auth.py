from pydantic import BaseModel, Field, ConfigDict
from uuid import UUID


class AuthToken(BaseModel):
    access_token:str
    refresh_token:str
    token_type:str
    tenant_id:UUID
    user_id:UUID
    role:UUID

class AuthCredential(BaseModel):

    username:str
    password:str

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "username": "test@gmail.com",
                "password": "wV#Y4H--L"
            }
        }
    )

class RefreshToken(BaseModel):

    refresh_token:str