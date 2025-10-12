from pydantic import BaseModel, Field, ConfigDict


class AuthToken(BaseModel):
    access_token:str
    refresh_token:str
    token_type:str

class AuthCredential(BaseModel):

    username:str
    password:str

class RefreshToken(BaseModel):

    refresh_token:str