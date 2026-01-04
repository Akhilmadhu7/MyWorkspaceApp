from sqlalchemy import (
    select
)
from sqlalchemy.ext.asyncio import AsyncSession
from database.models import Message
from enums import MessageStatusEnum, MessageTypeEnum
from uuid import UUID
from typing import List, Optional

class MessageRepository:

    def __init__(self, db:AsyncSession):
        self.db = db

    async def create(self, payload:dict) -> Message:
        message = Message(**payload)
        self.db.add(message)
        await self.db.commit()
        return message

    async def get_messages(self, tenant_id:UUID, sender_id:UUID, reciever_id:UUID) -> List[Message]:
        query = select(Message).where(
            Message.tenant_id == tenant_id,
            Message.receiver_id
        )

