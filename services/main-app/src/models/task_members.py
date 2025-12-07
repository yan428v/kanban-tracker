from sqlalchemy import Column, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID

from .base import BaseModelMixin, Base


class TaskMember(Base, BaseModelMixin):
    __tablename__ = "task_members"

    user_id = Column(
        UUID,
        nullable=False
    )

    task_id = Column(
        UUID,
        ForeignKey("task.id", ondelete="CASCADE"),
        nullable=False
    )

    task = relationship(
        "Task",
        back_populates="task_members"
    )

    __table_args__ = (
        UniqueConstraint('task_id', 'user_id', name='uq_task_member_task_user'),
    )


