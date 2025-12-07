from sqlalchemy import Column, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID

from .base import BaseModelMixin, Base


class Permission(Base, BaseModelMixin):
    __tablename__ = "permission"

    user_id = Column(
        UUID,
        nullable=False
    )

    board_id = Column(
        UUID,
        ForeignKey("board.id", ondelete="CASCADE"),
        nullable=False
    )

    board = relationship(
        "Board",
        back_populates="permissions",
    )

    __table_args__ = (
        UniqueConstraint('board_id', 'user_id', name='uq_permission_board_user'),
    )