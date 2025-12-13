import uuid

import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models import Team


@pytest.mark.asyncio(loop_scope="session")
async def test_create_team_no_name(default_auth_client: AsyncClient):
    response = await default_auth_client.post("/api/v1/teams", json={})
    assert response.status_code == 422
    data = response.json()
    assert data == {
        "detail": [
            {
                "type": "missing",
                "loc": ["body", "name"],
                "msg": "Field required",
                "input": {},
            }
        ]
    }


@pytest.mark.asyncio(loop_scope="session")
async def test_create_team_name_only(
    default_auth_client: AsyncClient, db_session: AsyncSession
):
    response = await default_auth_client.post(
        "/api/v1/teams", json={"name": "Test Team"}
    )
    assert response.status_code == 201
    data = response.json()

    team_id = uuid.UUID(data["id"])
    result = await db_session.execute(select(Team).where(Team.id == team_id))
    team_in_db = result.scalar_one()

    expected_response = {
        "id": str(team_in_db.id),
        "name": team_in_db.name,
        "description": team_in_db.description,
        "created_at": team_in_db.created_at.isoformat(),
        "updated_at": team_in_db.updated_at.isoformat(),
    }
    assert data == expected_response

    assert team_in_db.name == "Test Team"
    assert team_in_db.description is None


@pytest.mark.asyncio(loop_scope="session")
async def test_create_team_name_and_description(
    default_auth_client: AsyncClient, db_session: AsyncSession
):
    response = await default_auth_client.post(
        "/api/v1/teams", json={"name": "Test Team", "description": "Test Description"}
    )
    assert response.status_code == 201
    data = response.json()

    team_id = uuid.UUID(data["id"])
    result = await db_session.execute(select(Team).where(Team.id == team_id))
    team_in_db = result.scalar_one()

    expected_response = {
        "id": str(team_in_db.id),
        "name": team_in_db.name,
        "description": team_in_db.description,
        "created_at": team_in_db.created_at.isoformat(),
        "updated_at": team_in_db.updated_at.isoformat(),
    }
    assert data == expected_response

    assert team_in_db.name == "Test Team"
    assert team_in_db.description == "Test Description"
