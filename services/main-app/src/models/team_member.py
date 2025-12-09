from sqlalchemy import Column, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from .base import Base, BaseModelMixin


class TeamMember(Base, BaseModelMixin):
    __tablename__ = "team_member"
    __table_args__ = (
        UniqueConstraint("user_id", "team_id", name="uq_team_member_user_id_team_id"),
    )

    team_id = Column(UUID, ForeignKey("team.id", ondelete="CASCADE"), nullable=False)

    user_id = Column(UUID, ForeignKey("user.id", ondelete="CASCADE"), nullable=False)

    team = relationship(
        "Team",
        back_populates="team_members",
    )

    user = relationship("User", back_populates="team_member")
