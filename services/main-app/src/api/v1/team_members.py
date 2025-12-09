from uuid import UUID

from fastapi import APIRouter, Depends, Query, status

from models import TeamMember
from schemas.team_member import CreateTeamMemberRequest, TeamMemberResponse
from services.team_member import TeamMemberService, get_team_member_service

router = APIRouter()


@router.get("/team-members", response_model=list[TeamMemberResponse])
async def list_team_members(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=0, le=1000),
    team_id: UUID | None = None,
    user_id: UUID | None = None,
    service: TeamMemberService = Depends(get_team_member_service),
):
    members = await service.get_many(
        skip=skip,
        limit=limit,
        team_id=team_id,
        user_id=user_id,
    )
    return [team_member_to_response(member) for member in members]


@router.post(
    "/team-members",
    response_model=TeamMemberResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_team_member(
    payload: CreateTeamMemberRequest,
    service: TeamMemberService = Depends(get_team_member_service),
):
    member = await service.create(payload)
    return team_member_to_response(member)


@router.delete("/team-members", status_code=status.HTTP_204_NO_CONTENT)
async def delete_team_member(
    team_id: UUID,
    user_id: UUID,
    service: TeamMemberService = Depends(get_team_member_service),
):
    await service.delete(team_id=team_id, user_id=user_id)


def team_member_to_response(member: TeamMember) -> TeamMemberResponse:
    return TeamMemberResponse(
        id=member.id,
        team_id=member.team_id,
        user_id=member.user_id,
        created_at=member.created_at,
        updated_at=member.updated_at,
    )
