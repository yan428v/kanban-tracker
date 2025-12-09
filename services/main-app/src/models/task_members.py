from sqlalchemy import Column, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from .base import Base, BaseModelMixin


class TaskMember(Base, BaseModelMixin):
    __tablename__ = "task_members"

    user_id = Column(UUID, ForeignKey("user.id", ondelete="CASCADE"), nullable=False)

    task_id = Column(UUID, ForeignKey("task.id", ondelete="CASCADE"), nullable=False)

    user = relationship("User", back_populates="task_members")

    task = relationship("Task", back_populates="task_members")
