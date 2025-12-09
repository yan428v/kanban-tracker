import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase, declarative_mixin


class Base(DeclarativeBase):
    pass


@declarative_mixin
class BaseModelMixin:
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    created_at = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,  # todo чатик пишет что лучше использовать func.now()
    )

    updated_at = Column(
        DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow
    )
