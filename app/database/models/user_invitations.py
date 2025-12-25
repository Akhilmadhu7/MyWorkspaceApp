from sqlalchemy import (
    select,
    String,
    Boolean,
    Text,
    Column,
    UUID,
    ForeignKey,
    DateTime,
    func
)
from .base import Base
from datetime import datetime, timezone
from sqlalchemy.orm import relationship
import uuid


class UserInvitation(Base):

    __tablename__ = "user_invitations"

    user_invitation_id = Column(UUID(as_uuid=True),primary_key=True, unique=True, nullable=False, index=True, default=uuid.uuid4)
    user_invitation_email = Column(String(200), nullable=False, unique=True, index=True)
    user_invitation_first_name= Column(String(100), nullable=False)
    user_invitation_last_name = Column(String(100), nullable=True)
    user_invitation_role = Column(ForeignKey("roles.role_id", ondelete='CASCADE'), nullable=False)
    user_invitation_tenant_id = Column(ForeignKey("tenants.tenant_id", ondelete='CASCADE'), nullable=False, index=True)
    is_user_invitation_accepted = Column(Boolean, default=False)
    user_invitation_designation = Column(String(50), nullable=True)
    created_by = Column(ForeignKey("users.user_id", ondelete="SET NULL"), nullable=False)
    updated_by = Column(ForeignKey("users.user_id", ondelete="SET NULL"), nullable=False)
    created_at = Column(
        DateTime(timezone=True),
        default=lambda:datetime.now(timezone.utc),
        server_default=func.now()
    )
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda:datetime.now(timezone.utc),
        onupdate=lambda:datetime.now(timezone.utc),
        server_default=func.now()
    )

    tenant = relationship("Tenant")
    role = relationship("Role")

