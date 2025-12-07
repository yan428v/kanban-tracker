from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from models import Team
from schemas.team import TeamCreateRequest, TeamUpdateRequest, TeamResponse
from services.team import TeamService, get_team_service
from exceptions import TeamNotFoundError

router = APIRouter()

TEAM_NOT_FOUND_MESSAGE = "Team not found"


@router.get("/teams", response_model=List[TeamResponse])
async def list_teams(
    skip: int = 0,
    limit: int = 100,
    service: TeamService = Depends(get_team_service),
):
    teams = await service.get_many(skip=skip, limit=limit)
    return [team_to_response(team) for team in teams]


@router.get("/teams/{team_id}", response_model=TeamResponse)
async def get_team(
    team_id: UUID,
    service: TeamService = Depends(get_team_service),
):
    try:
        team = await service.get(team_id)
    except TeamNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=TEAM_NOT_FOUND_MESSAGE
        )
    return team_to_response(team)


@router.post("/teams", response_model=TeamResponse, status_code=status.HTTP_201_CREATED)
async def create_team(
    team_data: TeamCreateRequest,
    service: TeamService = Depends(get_team_service),
):
    team = await service.create(team_data)
    return team_to_response(team)


@router.patch("/teams/{team_id}", response_model=TeamResponse)
async def update_team(
    team_id: UUID,
    team_data: TeamUpdateRequest,
    service: TeamService = Depends(get_team_service),
):
    try:
        team = await service.update(team_id, team_data)
    except TeamNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=TEAM_NOT_FOUND_MESSAGE
        )
    return team_to_response(team)


@router.delete("/teams/{team_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_team(
    team_id: UUID,
    service: TeamService = Depends(get_team_service),
):
    try:
        await service.delete(team_id)
    except TeamNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=TEAM_NOT_FOUND_MESSAGE
        )


def team_to_response(team: Team) -> TeamResponse:
    return TeamResponse(
        id=team.id,
        name=team.name,
        description=team.description,
        created_at=team.created_at,
        updated_at=team.updated_at,
    )
