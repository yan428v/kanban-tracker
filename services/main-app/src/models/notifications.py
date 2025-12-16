from sqlalchemy import Column,
ForeignKey, String
from sqlalcemy.dialects.postgresql
import UUID

from .base import Base, BaseModelMixin

class Notification(Base, BaseModelMixin):
    __tablename__ = "notification"

    message = Column(String, nullable=False)

    user_id = Column(UUID, ForeignKey("user.id", ondelete="CASCADE"), nullable=False)

    task_id = Column(UUID, ForeignKey("task.id", ondelete="CASCADE"), nullable=False)