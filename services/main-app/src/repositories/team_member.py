from uuid import UUID

from fastapi import Depends
from sqlalchemy import delete, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_session
from exceptions import TeamMemberConflictError, TeamNotFoundError, UserNotFoundError
from models import TeamMember


class TeamMemberRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, team_member: TeamMember) -> TeamMember:
        self.db.add(team_member)
        try:
            await self.db.commit()
        except IntegrityError as e:
            await self.db.rollback()
            error_str = str(e.orig)
            if "uq_team_member_user_id_team_id" in error_str:
                raise TeamMemberConflictError(
                    team_member.team_id, team_member.user_id
                ) from e
            if "team_id" in error_str and "foreign key" in error_str.lower():
                raise TeamNotFoundError(team_member.team_id) from e
            if "user_id" in error_str and "foreign key" in error_str.lower():
                raise UserNotFoundError(team_member.user_id) from e
            raise
        await self.db.refresh(team_member)
        return team_member

    async def get_many(
        self,
        skip: int = 0,
        limit: int = 100,
        team_id: UUID | None = None,
        user_id: UUID | None = None,
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
            TeamMember.team_id == team_id, TeamMember.user_id == user_id
        )
        await self.db.execute(stmt)
        await self.db.commit()


async def get_team_member_repository(
    db: AsyncSession = Depends(get_session),
) -> TeamMemberRepository:
    return TeamMemberRepository(db)
