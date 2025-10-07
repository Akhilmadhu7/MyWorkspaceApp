from sqlalchemy import Column, UUID, String, Boolean, DateTime, text, func,Text
from datetime import datetime, timezone
from .base import Base
import uuid

class Tenant(Base):

    __tablename__ = 'tenants'

    tenant_id = Column(UUID(as_uuid=True), index=True, primary_key=True, nullable=False, unique=True, default=uuid.uuid4)
    tenant_name = Column(String(100), nullable=False)
    tenant_code = Column(String(15), nullable=False, unique=True)
    tenant_email = Column(String(200), nullable=False, unique=True)
    timezone = Column(String(50), nullable=False, default='UTC')
    tenant_logo = Column(Text, nullable=True)
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
        default=lambda: datetime.now(timezone.utc),
        server_default=func.now()
    )
