from sqlalchemy import ForeignKey, Column, UniqueConstraint
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
        nullable=False
    )

    team = relationship(
        "Team",
        back_populates="team_members",
    )

    __table_args__ = (
        UniqueConstraint('team_id', 'user_id', name='uq_team_member_team_user'),
    )