from uuid import UUID

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_session
from exceptions import TeamNotFoundError
from models import Team


class TeamRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, team_id: UUID) -> Team:
        result = await self.db.execute(select(Team).where(Team.id == team_id))
        team = result.scalar_one_or_none()
        if not team:
            raise TeamNotFoundError(team_id)
        return team

    async def get_all(self, skip: int = 0, limit: int = 100) -> list[Team]:
        result = await self.db.execute(select(Team).offset(skip).limit(limit))
        return result.scalars().all()

    async def create(self, team: Team) -> Team:
        self.db.add(team)
        await self.db.commit()
        await self.db.refresh(team)
        return team

    async def update(self, team: Team) -> Team:
        await self.db.commit()
        await self.db.refresh(team)
        return team

    async def delete(self, team: Team) -> None:
        await self.db.delete(team)
        await self.db.commit()


async def get_team_repository(
    db: AsyncSession = Depends(get_session),
) -> TeamRepository:
    return TeamRepository(db)
