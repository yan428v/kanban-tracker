from sqlalchemy import Boolean, Column, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from .base import Base, BaseModelMixin


class Board(Base, BaseModelMixin):
    __tablename__ = "board"

    title = Column(String, nullable=False)

    description = Column(String, nullable=True)

    is_public = Column(Boolean, nullable=False, default=False)

    owner_id = Column(UUID, ForeignKey("user.id", ondelete="CASCADE"), nullable=False)

    team_id = Column(UUID, ForeignKey("team.id", ondelete="CASCADE"), nullable=True)

    owner = relationship(
        "User",
        back_populates="boards",
    )

    columns = relationship(
        "BoardColumn", back_populates="board", cascade="all, delete-orphan"
    )

    team = relationship("Team", back_populates="boards")
