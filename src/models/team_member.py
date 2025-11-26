from sqlalchemy import ForeignKey, Column
from sqlalchemy.orm import relationship
from .base import BaseModelMixin, Base
from sqlalchemy.dialects.postgresql import UUID


class TeamMember(Base, BaseModelMixin):
    __tablename__ = "team_member"

    team_id = Column(
        UUID,
        ForeignKey('team.id', ondelete='CASCADE'),
        nullable=False
    )

    user_id = Column(
        UUID,
        ForeignKey('user.id', ondelete="CASCADE"),
        nullable=False
    )

    team = relationship(
        "Team",
        back_populates="team_members",
    )

    user = relationship(
        "User",
        back_populates="team_member"
    )