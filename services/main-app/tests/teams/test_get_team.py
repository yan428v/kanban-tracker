import uuid

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from models import Team


@pytest.mark.asyncio(loop_scope="session")
async def test_get_team_not_found(test_client: AsyncClient):
    non_existent_id = uuid.uuid4()
    response = await test_client.get(f"/api/v1/teams/{non_existent_id}")
    assert response.status_code == 404
    assert response.json() == {"detail": "Team not found"}


@pytest.mark.asyncio(loop_scope="session")
async def test_get_team_success(test_client: AsyncClient, db_session: AsyncSession):
    team = Team(name="Test Team", description="Test Description")
    db_session.add(team)
    await db_session.commit()
    await db_session.refresh(team)

    response = await test_client.get(f"/api/v1/teams/{team.id}")
    assert response.status_code == 200
    data = response.json()

    expected = {
        "id": str(team.id),
        "name": team.name,
        "description": team.description,
        "created_at": team.created_at.isoformat(),
        "updated_at": team.updated_at.isoformat(),
    }
    assert data == expected
