from sqlalchemy import Column, String
from sqlalchemy.orm import relationship
from .base import Base, BaseModelMixin


class User(Base, BaseModelMixin):
    __tablename__ = "user"

    name = Column(
        String,
        nullable=False
    )

    email = Column(
        String,
        nullable=False,
        unique=True
    )

    password_hash = Column(
        String,
        nullable=False
    )

    photo = Column(
        String,
        nullable=True
    )

    tasks = relationship(
        "Task",
        back_populates="user",
        cascade="all, delete-orphan"
    )

    comments = relationship(
        "Comment",
        back_populates="user",
        cascade="all, delete-orphan"
    )

    team_member = relationship(
        "TeamMember",
        back_populates="user",
        cascade="all, delete-orphan"

    )

    boards = relationship(
        "Board",
        back_populates="owner",
        cascade="all, delete-orphan"

    )



    def __repr__(self):
        return f"<User(id={self.id}, name='{self.name}', email={self.email})>"