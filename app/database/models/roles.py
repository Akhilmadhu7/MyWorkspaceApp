from sqlalchemy import (
    Column,
    UUID,
    String,
    DateTime,
    func
)
from datetime import datetime, timezone
from .base import Base
import uuid


class Role(Base):
    __tablename__ = 'roles'

    role_id = Column(UUID(as_uuid=True), index=True, primary_key=True, nullable=False, unique=True, default=uuid.uuid4)
    role_code = Column(String(50), nullable=False, unique=True)
    role_name = Column(String(50), nullable=False, unique=True, index=True)
    role_created_at = Column(
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
