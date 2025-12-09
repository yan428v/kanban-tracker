from sqlalchemy import Column, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from .base import Base, BaseModelMixin


class Comment(Base, BaseModelMixin):
    __tablename__ = "comment"

    body = Column(String, nullable=False)

    user_id = Column(UUID, ForeignKey("user.id", ondelete="CASCADE"), nullable=False)

    task_id = Column(UUID, ForeignKey("task.id", ondelete="CASCADE"), nullable=False)

    user = relationship("User", back_populates="comments")

    task = relationship("Task", back_populates="comments")
