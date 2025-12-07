from sqlalchemy import Column, String, Enum, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from enums.task_status import TaskStatus

from .base import Base, BaseModelMixin
from sqlalchemy.dialects.postgresql import UUID

class Task(Base, BaseModelMixin):
    __tablename__ = "task"

    title = Column(
        String,
        nullable=False
    )

    description = Column(
        String,
        nullable=True
    )

    status = Column(
        Enum(TaskStatus),
        nullable=False,
        default=TaskStatus.PENDING
    )

    due_date = Column(
        DateTime,
        nullable=True
    )

    user_id = Column(
        UUID,
        nullable=False
    )

    column_id = Column(
        UUID,
        ForeignKey("column.id", ondelete="CASCADE"),
        nullable=False
    )

    comments = relationship(
        "Comment",
        back_populates="task",
        cascade="all, delete-orphan"

    )

    column = relationship(
        "BoardColumn",
        back_populates="tasks"
    )

    task_members = relationship(
        "TaskMember",
        back_populates="task"
    )

    def __repr__(self):
        return f"<Task(id={self.id}, title='{self.title}', status={self.status})>"