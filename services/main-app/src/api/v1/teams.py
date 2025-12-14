from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status

from auth.dependencies import get_current_user
from exceptions import TeamNotFoundError
from models import Team, User
from schemas.team import CreateTeamRequest, TeamResponse, UpdateTeamRequest
from services.team import TeamService, get_team_service

router = APIRouter()

TEAM_NOT_FOUND_MESSAGE = "Team not found"


@router.get("/teams", response_model=list[TeamResponse])
async def list_teams(
    skip: int | None = Query(None),
    limit: int | None = Query(None),
    service: TeamService = Depends(get_team_service),
    current_user: User = Depends(get_current_user),
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

    teams = await service.get_many(skip=skip, limit=limit)
    return [team_to_response(team) for team in teams]


@router.get("/teams/{team_id}", response_model=TeamResponse)
async def get_team(
    team_id: UUID,
    service: TeamService = Depends(get_team_service),
    current_user: User = Depends(get_current_user),
):
    try:
        team = await service.get(team_id)
    except TeamNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=TEAM_NOT_FOUND_MESSAGE
        ) from e
    return team_to_response(team)


@router.post("/teams", response_model=TeamResponse, status_code=status.HTTP_201_CREATED)
async def create_team(
    team_data: CreateTeamRequest,
    service: TeamService = Depends(get_team_service),
    current_user: User = Depends(get_current_user),
):
    team = await service.create(team_data)
    return team_to_response(team)


@router.patch("/teams/{team_id}", response_model=TeamResponse)
async def update_team(
    team_id: UUID,
    team_data: UpdateTeamRequest,
    service: TeamService = Depends(get_team_service),
    current_user: User = Depends(get_current_user),
):
    try:
        team = await service.update(team_id, team_data)
    except TeamNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=TEAM_NOT_FOUND_MESSAGE
        ) from e
    return team_to_response(team)


@router.delete("/teams/{team_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_team(
    team_id: UUID,
    service: TeamService = Depends(get_team_service),
    current_user: User = Depends(get_current_user),
):
    try:
        await service.delete(team_id)
    except TeamNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=TEAM_NOT_FOUND_MESSAGE
        ) from e


def team_to_response(team: Team) -> TeamResponse:
    return TeamResponse(
        id=team.id,
        name=team.name,
        description=team.description,
        created_at=team.created_at,
        updated_at=team.updated_at,
    )
