from uuid import UUID

from fastapi import Depends

from models import TeamMember
from repositories.team_member import (
    TeamMemberRepository,
    get_team_member_repository,
)
from schemas.team_member import CreateTeamMemberRequest


class TeamMemberService:
    def __init__(self, repository: TeamMemberRepository):
        self.repository = repository

    async def create(self, data: CreateTeamMemberRequest) -> TeamMember:
        team_member = TeamMember(
            team_id=data.team_id,
            user_id=data.user_id,
        )
        return await self.repository.create(team_member)

    async def get_many(
        self,
        skip: int = 0,
        limit: int = 100,
        team_id: UUID | None = None,
        user_id: UUID | None = None,
    ) -> list[TeamMember]:
        return await self.repository.get_many(
            skip=skip,
            limit=limit,
            team_id=team_id,
            user_id=user_id,
        )

    async def delete(self, team_id: UUID, user_id: UUID) -> None:
        await self.repository.delete(team_id, user_id)


async def get_team_member_service(
    repository: TeamMemberRepository = Depends(get_team_member_repository),
) -> TeamMemberService:
    return TeamMemberService(repository)
