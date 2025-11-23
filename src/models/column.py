from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID

from .base import Base,BaseModelMixin


class BoardColumn(Base, BaseModelMixin): # хотел назвать Column, но он думал что это из алхимии берется Column
    __tablename__ = "column"

    title = Column(
        String,
        nullable=False
    )

    position = Column(
        Integer,
        default=0
    )

    limit = Column(
        Integer,
        nullable=True
    )

    board_id = Column(
        UUID,
        ForeignKey("board.id", ondelete="CASCADE"),
        nullable=False
    )

    board = relationship(
        "Board",
        back_populates="columns"
    )

    tasks = relationship(
        "Task",
        back_populates="column",
        cascade="all, delete-orphan"
    )