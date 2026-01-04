from .base import Base
from sqlalchemy import (
    BigInteger, BIGINT,
    Text,
    String,
    Boolean,
    Column,
    DateTime,
    Enum,
    ForeignKey,
    UUID as PG_UUID,
    func
)
from enums import MessageStatusEnum, MessageTypeEnum
from datetime import datetime, timezone

class Message(Base):

    __tablename__ = "messages"
    message_id = Column(BigInteger, primary_key=True, autoincrement=True)
    tenant_id = Column(PG_UUID(as_uuid=True),ForeignKey("tenants.tenant_id", ondelete='CASCADE'), nullable=False, index=True)
    sender_id = Column(
        PG_UUID(as_uuid=True),
        ForeignKey("users.user_id", ondelete='SET NULL'),
        nullable=True,
        index=True
    )
    receiver_id = Column(
        PG_UUID(as_uuid=True),
        ForeignKey('users.user_id', ondelete='SET NULL'),
        nullable=True,
        index=True
    )
    message = Column(Text, nullable=False)
    message_status = Column(Enum(MessageStatusEnum), default=MessageStatusEnum.SENT, nullable=False)
    message_type = Column(Enum(MessageTypeEnum), default=MessageTypeEnum.TEXT, nullable=False)
    created_at = Column(
        DateTime(timezone=True), 
        default=lambda: datetime.now(timezone.utc), 
        server_default=func.now()
    )

    def to_dict(self) -> dict:
        return {
            "message_id": self.message_id,
            "sender_id": str(self.sender_id) if self.sender_id else None,
            "receiver_id": str(self.receiver_id) if self.receiver_id else None,
            "message": self.message,
            "message_status": str(self.message_status.value),
            "message_type": str(self.message_type.value),
            "created_at": self.created_at.isoformat() if self.created_at else None
        }
