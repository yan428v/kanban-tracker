from uuid import UUID

from fastapi import Depends

from models import Team
from repositories.team import TeamRepository, get_team_repository
from schemas.team import CreateTeamRequest, UpdateTeamRequest


class TeamService:
    def __init__(self, repository: TeamRepository):
        self.repository = repository

    async def get(self, team_id: UUID) -> Team:
        return await self.repository.get_by_id(team_id)

    async def get_many(self, skip: int = 0, limit: int = 100) -> list[Team]:
        return await self.repository.get_all(skip=skip, limit=limit)

    async def create(self, team_data: CreateTeamRequest) -> Team:
        team = Team(name=team_data.name, description=team_data.description)
        return await self.repository.create(team)

    async def update(
        self, team_id: UUID, team_data: UpdateTeamRequest
    ) -> Team:
        team = await self.repository.get_by_id(team_id)

        if team_data.name is not None:
            team.name = team_data.name
        if team_data.description is not None:
            team.description = team_data.description

        return await self.repository.update(team)

    async def delete(self, team_id: UUID) -> None:
        team = await self.repository.get_by_id(team_id)
        await self.repository.delete(team)


async def get_team_service(
    repository: TeamRepository = Depends(get_team_repository),
) -> TeamService:
    return TeamService(repository)
