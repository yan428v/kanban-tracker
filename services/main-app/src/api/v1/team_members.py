from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from models import TeamMember
from schemas.team_member import TeamMemberCreateRequest, TeamMemberResponse
from services.team_member import TeamMemberService, get_team_member_service
from exceptions import TeamMemberNotFoundError, TeamMemberDuplicateError

router = APIRouter()

TEAM_MEMBER_NOT_FOUND_MESSAGE = "Team member not found"
TEAM_MEMBER_DUPLICATE_MESSAGE = "User is already a member of this team"


@router.get("/team-members", response_model=List[TeamMemberResponse])
async def list_team_members(
    skip: int = 0,
    limit: int = 100,
    service: TeamMemberService = Depends(get_team_member_service),
):
    team_members = await service.get_many(skip=skip, limit=limit)
    return [team_member_to_response(tm) for tm in team_members]


@router.get("/teams/{team_id}/members", response_model=List[TeamMemberResponse])
async def get_team_members_by_team(
    team_id: UUID,
    skip: int = 0,
    limit: int = 100,
    service: TeamMemberService = Depends(get_team_member_service),
):
    team_members = await service.get_by_team_id(team_id, skip=skip, limit=limit)
    return [team_member_to_response(tm) for tm in team_members]


@router.post(
    "/team-members",
    response_model=TeamMemberResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_team_member(
    team_member_data: TeamMemberCreateRequest,
    service: TeamMemberService = Depends(get_team_member_service),
):
    try:
        team_member = await service.create(team_member_data)
    except TeamMemberDuplicateError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail=TEAM_MEMBER_DUPLICATE_MESSAGE
        )
    return team_member_to_response(team_member)


@router.delete("/team-members/{team_member_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_team_member(
    team_member_id: UUID,
    service: TeamMemberService = Depends(get_team_member_service),
):
    try:
        await service.delete(team_member_id)
    except TeamMemberNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=TEAM_MEMBER_NOT_FOUND_MESSAGE
        )


def team_member_to_response(team_member: TeamMember) -> TeamMemberResponse:
    return TeamMemberResponse(
        id=team_member.id,
        team_id=team_member.team_id,
        user_id=team_member.user_id,
        created_at=team_member.created_at,
        updated_at=team_member.updated_at,
    )
