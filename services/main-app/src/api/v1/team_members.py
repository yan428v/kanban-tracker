from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status

from models import TeamMember
from schemas.team_member import (
    CreateTeamMemberRequest,
    DeleteTeamMemberRequest,
    TeamMemberResponse,
)
from services.team_member import TeamMemberService, get_team_member_service

router = APIRouter()


@router.get("/team-members", response_model=list[TeamMemberResponse])
async def list_team_members(
    skip: int | None = Query(None),
    limit: int | None = Query(None),
    team_id: UUID | None = Query(None),
    user_id: UUID | None = Query(None),
    service: TeamMemberService = Depends(get_team_member_service),
):
    if skip is None:
        skip = 0
    elif skip < 0:
        skip = 0

    if limit is None:
        limit = 100
    else:
        if limit < 1:
            limit = 100
        elif limit > 1000:
            limit = 1000

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


@router.delete("/team-members", status_code=status.HTTP_200_OK)
async def delete_team_member(
    payload: DeleteTeamMemberRequest,
    service: TeamMemberService = Depends(get_team_member_service),
):
    if payload.team_id is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="team_id is required",
        )
    if payload.user_id is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="user_id is required",
        )
    await service.delete(team_id=payload.team_id, user_id=payload.user_id)


def team_member_to_response(member: TeamMember) -> TeamMemberResponse:
    return TeamMemberResponse(
        id=member.id,
        team_id=member.team_id,
        user_id=member.user_id,
        created_at=member.created_at,
        updated_at=member.updated_at,
    )
