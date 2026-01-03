from pydantic import BaseModel,Field
from uuid import UUID
from enums import EventEnum


class OneToOneChatSchema(BaseModel):

    target_user_id: UUID
    message:str = Field(min_length=1)
    type:EventEnum = Field(default=EventEnum.CHAT_MESSAGE.value)


    

