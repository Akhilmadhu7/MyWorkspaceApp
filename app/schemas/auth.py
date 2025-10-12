from pydantic import BaseModel, Field, ConfigDict

class AuthCredential(BaseModel):

    username:str
    password:str
    