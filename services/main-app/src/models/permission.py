from sqlalchemy import Column, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from .base import Base, BaseModelMixin


class Permission(Base, BaseModelMixin):
    __tablename__ = "permission"

    user_id = Column(UUID, ForeignKey("user.id", ondelete="CASCADE"), nullable=False)

    board_id = Column(UUID, ForeignKey("board.id", ondelete="CASCADE"), nullable=False)

    user = relationship("User", back_populates="permission")

    board = relationship(
        "Board",
        back_populates="permissions",
    )
