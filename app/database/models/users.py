from sqlalchemy import (
    Column,
    String,
    Text,
    func,
    UUID,
    DateTime,
    ForeignKey,
    Boolean,
    Date
)
from .base import Base
from datetime import datetime, timezone
from sqlalchemy.orm import relationship
import uuid


class User(Base):

    __tablename__ = 'users'

    user_id = Column(UUID(as_uuid=True), primary_key=True, unique=True, index=True,nullable=False, default=uuid.uuid4)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=True)
    email = Column(String(200), nullable=False, unique=True)
    username = Column(String(200), nullable=False, unique=True)
    image_url = Column(Text, nullable=True)
    tenant_id = Column(ForeignKey("tenants.tenant_id", ondelete='CASCADE'), nullable=False, index=True)
    role_id = Column(ForeignKey("roles.role_id", ondelete='CASCADE'), nullable=False)
    designation = Column(String(50), nullable=True)
    date_of_birth = Column(Date, nullable=True)
    password = Column(String(200), nullable=False)
    is_authenticated = Column(Boolean, default=False)
    is_blocked = Column(Boolean, default=False)
    is_active = Column(Boolean, default=False)
    is_deleted = Column(Boolean, default=False)
    created_at = Column(
        DateTime(timezone=True), 
        default=lambda: datetime.now(timezone.utc), 
        server_default=func.now()
    )
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        server_default=func.now()
    )
    soft_teleted_at = Column(
        DateTime(timezone=True),
        nullable=True
    )
    last_password_changed_at = Column(
        DateTime(timezone=True),
        nullable=True
    )

    tenant = relationship("Tenant")
    role = relationship("Role")