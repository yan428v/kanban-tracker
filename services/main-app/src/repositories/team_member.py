from typing import Optional
from uuid import UUID

from fastapi import Depends
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_session
from models import TeamMember


class TeamMemberRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, team_member: TeamMember) -> TeamMember:
        # TODO: check unique constraint error
        self.db.add(team_member)
        await self.db.commit()
        await self.db.refresh(team_member)
        return team_member

    async def get_many(
        self,
        skip: int = 0,
        limit: int = 100,
        team_id: Optional[UUID] = None,
        user_id: Optional[UUID] = None,
    ) -> list[TeamMember]:
        query = select(TeamMember)
        if team_id is not None:
            query = query.where(TeamMember.team_id == team_id)
        if user_id is not None:
            query = query.where(TeamMember.user_id == user_id)

        result = await self.db.execute(query.offset(skip).limit(limit))
        return result.scalars().all()

    async def delete(self, team_id: UUID, user_id: UUID) -> None:
        stmt = delete(TeamMember).where(
            TeamMember.team_id == team_id,
            TeamMember.user_id == user_id
        )
        await self.db.execute(stmt)
        await self.db.commit()


async def get_team_member_repository(
    db: AsyncSession = Depends(get_session),
) -> TeamMemberRepository:
    return TeamMemberRepository(db)
