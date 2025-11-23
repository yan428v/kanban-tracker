
from sqlalchemy import Column, String, Boolean, Enum, ForeignKey
from sqlalchemy.orm import relationship
from src.enums.board_colors import BoardColor
from sqlalchemy.dialects.postgresql import UUID

from .base import BaseModelMixin, Base


class Board(Base, BaseModelMixin):
    __tablename__ = "board"

    title = Column(
        String,
        nullable=False
    )

    description = Column(
        String,
        nullable=True
    )

    is_public = Column(
        Boolean,
        nullable=False,
        default=False
    )

    color = Column(
        Enum(BoardColor),
        nullable=False,
        default=BoardColor.WHITE
    )

    owner_id = Column(
        UUID,
        ForeignKey("user.id", ondelete="CASCADE"),
        nullable=False
    )

    team_id = Column(
        UUID,
        ForeignKey("team.id", ondelete="CASCADE"),
        nullable=True
    )

    owner = relationship(
        "User",
        back_populates="boards",
    )

    columns = relationship(
        "BoardColumn",
        back_populates="board",
        cascade="all, delete-orphan"
    )

    team = relationship(
        "Team",
        back_populates="boards"
    )

    permissions = relationship(
        "Permission",
        back_populates="board",
        cascade="all, delete-orphan"
    )
