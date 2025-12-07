from uuid import UUID

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from models import TeamMember
from core.database import get_session
from exceptions import TeamMemberNotFoundError, TeamMemberDuplicateError


class TeamMemberRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, team_member_id: UUID) -> TeamMember:
        result = await self.db.execute(
            select(TeamMember).where(TeamMember.id == team_member_id)
        )
        team_member = result.scalar_one_or_none()
        if not team_member:
            raise TeamMemberNotFoundError(team_member_id)
        return team_member

    async def get_all(self, skip: int = 0, limit: int = 100) -> list[TeamMember]:
        result = await self.db.execute(select(TeamMember).offset(skip).limit(limit))
        return result.scalars().all()

    async def get_by_team_id(
        self, team_id: UUID, skip: int = 0, limit: int = 100
    ) -> list[TeamMember]:
        result = await self.db.execute(
            select(TeamMember)
            .where(TeamMember.team_id == team_id)
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()

    async def get_by_user_id(
        self, user_id: UUID, skip: int = 0, limit: int = 100
    ) -> list[TeamMember]:
        result = await self.db.execute(
            select(TeamMember)
            .where(TeamMember.user_id == user_id)
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()

    async def create(self, team_member: TeamMember) -> TeamMember:
        self.db.add(team_member)
        try:
            await self.db.commit()
            await self.db.refresh(team_member)
            return team_member
        except IntegrityError as e:
            # TODO: is the actual error that is returned?
            await self.db.rollback()
            if "uq_team_member_team_user" in str(e.orig):
                raise TeamMemberDuplicateError(team_member.team_id, team_member.user_id)
            raise

    async def delete(self, team_member: TeamMember) -> None:
        # TODO: should be idempotent, but need to test
        await self.db.delete(team_member)
        await self.db.commit()


async def get_team_member_repository(
    db: AsyncSession = Depends(get_session),
) -> TeamMemberRepository:
    return TeamMemberRepository(db)
