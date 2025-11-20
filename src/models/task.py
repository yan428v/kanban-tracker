import enum

from sqlalchemy import Column, String, Enum, DateTime
from src.models import Base, BaseModelMixin
from src.enums import TaskStatus

class Task(Base, BaseModelMixin):
    __tablename__ = "tasks"

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
        Integer,
        ForeignKey('users.id', ondelete='CASCADE'),
        nullable=False
    )

    user = relationship(
        "User",
        back_populates="tasks"
    )

    def __repr__(self):
        return f"<Task(id={self.id}, title='{self.title}', status={self.status})>"