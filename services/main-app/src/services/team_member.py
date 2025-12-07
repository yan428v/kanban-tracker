from uuid import UUID

from fastapi import Depends

from models import TeamMember
from repositories.team_member import TeamMemberRepository, get_team_member_repository
from schemas.team_member import TeamMemberCreateRequest


class TeamMemberService:
    def __init__(self, repository: TeamMemberRepository):
        self.repository = repository

    async def get(self, team_member_id: UUID) -> TeamMember:
        return await self.repository.get_by_id(team_member_id)

    async def get_many(self, skip: int = 0, limit: int = 100) -> list[TeamMember]:
        return await self.repository.get_all(skip=skip, limit=limit)

    async def get_by_team_id(self, team_id: UUID, skip: int = 0, limit: int = 100) -> list[TeamMember]:
        return await self.repository.get_by_team_id(team_id, skip=skip, limit=limit)

    async def get_by_user_id(self, user_id: UUID, skip: int = 0, limit: int = 100) -> list[TeamMember]:
        return await self.repository.get_by_user_id(user_id, skip=skip, limit=limit)

    async def create(self, team_member_data: TeamMemberCreateRequest) -> TeamMember:
        team_member = TeamMember(
            team_id=team_member_data.team_id,
            user_id=team_member_data.user_id
        )
        return await self.repository.create(team_member)

    async def delete(self, team_member_id: UUID) -> None:
        team_member = await self.repository.get_by_id(team_member_id)
        await self.repository.delete(team_member)


async def get_team_member_service(
    repository: TeamMemberRepository = Depends(get_team_member_repository),
) -> TeamMemberService:
    return TeamMemberService(repository)

