from sqlalchemy import Column, String
from sqlalchemy.orm import relationship

from .base import Base, BaseModelMixin


class Team(Base, BaseModelMixin):
    __tablename__ = "team"

    name = Column(
        String,
        nullable=False
    )

    description = Column(
        String,
        nullable=True
    )

    team_members = relationship(
        "TeamMembers",
        back_populates="team",
        cascade="all, delete-orphan"
    )