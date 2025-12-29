from pydantic import BaseModel,Field
from uuid import UUID


class OneToOneChatSchema(BaseModel):

    target_user_id: UUID
    message:str = Field(min_length=1)
    

