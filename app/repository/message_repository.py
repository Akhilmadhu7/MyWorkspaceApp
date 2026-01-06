from sqlalchemy import (
    select,
    exists,
    update
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
        await self.db.refresh(message)
        return message.to_dict()

    async def non_delivered_message_exists(self, tenant_id:UUID, reciever_id:UUID) -> bool:
        query = select(
            exists().where(Message.message_status==MessageStatusEnum.SENT)
        )
        result = await self.db.execute(query)
        return bool(result.scalar())


    async def get_messages(
            self,
            tenant_id:UUID,
            message_status:List[MessageStatusEnum] = [MessageStatusEnum.SENT],
            filters:dict = {}
        ) -> List[dict]:

        query = select(Message).where(
            Message.tenant_id == tenant_id,
            Message.message_status.in_(message_status)
        )

        if filters.get("receiver_id", None):
            query = query.where(Message.receiver_id == filters.get("receiver_id"))
        
        if filters.get("sender_id", None):
            query = query.where(Message.sender_id == filters.get("sender_id"))
        result = await self.db.execute(query)
        messages = result.scalars().all()
        return [message.to_dict() for message in messages]

    async def bulk_update_status(self, tenant_id:UUID, message_ids: List[int], status: MessageStatusEnum) -> None:
        stmt = (
            update(Message)
            .where(Message.tenant_id == tenant_id, Message.message_id.in_(message_ids))
            .values(message_status=status)
            .execution_options(synchronize_session=False)
        )
        result = await self.db.execute(stmt)
        await self.db.commit()
        


