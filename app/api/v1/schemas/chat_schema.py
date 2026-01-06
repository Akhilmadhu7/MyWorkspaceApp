from pydantic import BaseModel,Field
from uuid import UUID
from enums import MessageTypeEnum, MessageStatusEnum
from typing import List


class OneToOneChatSchema(BaseModel):

    target_user_id: UUID
    message:str = Field(min_length=1)
    message_type:MessageTypeEnum = Field(default=MessageTypeEnum.TEXT.value)

class ChatAcknowldgementSchema(BaseModel):

    message_ids:List[int]
    message_status:MessageStatusEnum



    

