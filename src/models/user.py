from sqlalchemy import Column, String
from src.models import Base, BaseModelMixin


class User(Base, BaseModelMixin):
    __tablename__ = "users"

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

    def __repr__(self):
        return f"<User(id={self.id}, name='{self.name}', email={self.email})>"