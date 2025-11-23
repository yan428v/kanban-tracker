from sqlalchemy import Column, String, Enum, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from .base import Base, BaseModelMixin
from src.enums import TaskStatus
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
        ForeignKey('user.id', ondelete='CASCADE'),
        nullable=False
    )

    user = relationship(
        "User",
        back_populates="tasks"
    )

    comments = relationship(
        "Comment",
        back_populates="task",
        cascade="all, delete-orphan"

    )

    def __repr__(self):
        return f"<Task(id={self.id}, title='{self.title}', status={self.status})>"