import uuid

import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models import Team


@pytest.mark.asyncio(loop_scope="session")
async def test_delete_team_not_found(default_auth_client: AsyncClient):
    non_existent_id = uuid.uuid4()
    response = await default_auth_client.delete(f"/api/v1/teams/{non_existent_id}")
    assert response.status_code == 404
    assert response.json() == {"detail": "Team not found"}


@pytest.mark.asyncio(loop_scope="session")
async def test_delete_team_success(
    default_auth_client: AsyncClient, db_session: AsyncSession
):
    team = Team(name="Test Team", description="Test Description")
    db_session.add(team)
    await db_session.commit()
    team_id = team.id

    response = await default_auth_client.delete(f"/api/v1/teams/{team_id}")
    assert response.status_code == 204

    result = await db_session.execute(select(Team).where(Team.id == team_id))
    team_in_db = result.scalar_one_or_none()
    assert team_in_db is None
