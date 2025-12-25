from sqlalchemy import (
    String,
    UUID,
    Column,
    Enum,
    ForeignKey,
    DateTime,
    func
)
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from .base import Base
from enums import TokenTypeEnum
import uuid


class Token(Base):

    __tablename__ = 'tokens'

    token_id = Column(UUID(as_uuid=True), nullable=False, unique=True, primary_key=True, default=uuid.uuid4)
    token = Column(String(length=120), nullable=False, unique=True, index=True)
    token_tenant_id = Column(
        UUID(as_uuid=True),
        ForeignKey("tenants.tenant_id", ondelete='CASCADE'), nullable=False, index=True
    )
    token_type = Column(Enum(TokenTypeEnum), nullable=False)
    user_invitation_id = Column(
        UUID(as_uuid=True),
        ForeignKey("user_invitations.user_invitation_id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.user_id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )

    expires_at = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        server_default=func.now()
    )

    # optional relationships
    user_invitation = relationship("UserInvitation", backref="tokens")
    user = relationship("User", backref="tokens")
    tenant = relationship("Tenant")
