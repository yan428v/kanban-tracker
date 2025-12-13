import uuid

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from models import Team


@pytest.mark.asyncio(loop_scope="session")
async def test_update_team_not_found(test_client: AsyncClient):
    non_existent_id = uuid.uuid4()
    response = await test_client.patch(
        f"/api/v1/teams/{non_existent_id}", json={"name": "Updated Name"}
    )
    assert response.status_code == 404
    assert response.json() == {"detail": "Team not found"}


@pytest.mark.asyncio(loop_scope="session")
async def test_update_team_no_updates(
    test_client: AsyncClient, db_session: AsyncSession
):
    team = Team(name="Original Name", description="Original Description")
    db_session.add(team)
    await db_session.commit()
    await db_session.refresh(team)

    original_created_at = team.created_at

    response = await test_client.patch(f"/api/v1/teams/{team.id}", json={})
    assert response.status_code == 200
    data = response.json()

    await db_session.refresh(team)

    expected_response = {
        "id": str(team.id),
        "name": team.name,
        "description": team.description,
        "created_at": team.created_at.isoformat(),
        "updated_at": team.updated_at.isoformat(),
    }
    assert data == expected_response

    assert team.name == "Original Name"
    assert team.description == "Original Description"
    assert team.created_at == original_created_at


@pytest.mark.asyncio(loop_scope="session")
async def test_update_team_name_only(
    test_client: AsyncClient, db_session: AsyncSession
):
    team = Team(name="Original Name", description="Original Description")
    db_session.add(team)
    await db_session.commit()
    await db_session.refresh(team)

    original_created_at = team.created_at

    response = await test_client.patch(
        f"/api/v1/teams/{team.id}", json={"name": "Updated Name"}
    )
    assert response.status_code == 200
    data = response.json()

    await db_session.refresh(team)

    expected_response = {
        "id": str(team.id),
        "name": team.name,
        "description": team.description,
        "created_at": team.created_at.isoformat(),
        "updated_at": team.updated_at.isoformat(),
    }
    assert data == expected_response

    expected_db_team = {
        "id": team.id,
        "name": "Updated Name",
        "description": "Original Description",
        "created_at": original_created_at,
        "updated_at": team.updated_at,
    }
    assert {
        "id": team.id,
        "name": team.name,
        "description": team.description,
        "created_at": team.created_at,
        "updated_at": team.updated_at,
    } == expected_db_team


@pytest.mark.asyncio(loop_scope="session")
async def test_update_team_description_only(
    test_client: AsyncClient, db_session: AsyncSession
):
    team = Team(name="Original Name", description="Original Description")
    db_session.add(team)
    await db_session.commit()
    await db_session.refresh(team)

    original_created_at = team.created_at

    response = await test_client.patch(
        f"/api/v1/teams/{team.id}", json={"description": "Updated Description"}
    )
    assert response.status_code == 200
    data = response.json()

    await db_session.refresh(team)

    expected_response = {
        "id": str(team.id),
        "name": team.name,
        "description": team.description,
        "created_at": team.created_at.isoformat(),
        "updated_at": team.updated_at.isoformat(),
    }
    assert data == expected_response

    expected_db_team = {
        "id": team.id,
        "name": "Original Name",
        "description": "Updated Description",
        "created_at": original_created_at,
        "updated_at": team.updated_at,
    }
    assert {
        "id": team.id,
        "name": team.name,
        "description": team.description,
        "created_at": team.created_at,
        "updated_at": team.updated_at,
    } == expected_db_team


@pytest.mark.asyncio(loop_scope="session")
async def test_update_team_multiple_fields(
    test_client: AsyncClient, db_session: AsyncSession
):
    team = Team(name="Original Name", description="Original Description")
    db_session.add(team)
    await db_session.commit()
    await db_session.refresh(team)

    original_created_at = team.created_at

    response = await test_client.patch(
        f"/api/v1/teams/{team.id}",
        json={"name": "Updated Name", "description": "Updated Description"},
    )
    assert response.status_code == 200
    data = response.json()

    await db_session.refresh(team)

    expected_response = {
        "id": str(team.id),
        "name": team.name,
        "description": team.description,
        "created_at": team.created_at.isoformat(),
        "updated_at": team.updated_at.isoformat(),
    }
    assert data == expected_response

    expected_db_team = {
        "id": team.id,
        "name": "Updated Name",
        "description": "Updated Description",
        "created_at": original_created_at,
        "updated_at": team.updated_at,
    }
    assert {
        "id": team.id,
        "name": team.name,
        "description": team.description,
        "created_at": team.created_at,
        "updated_at": team.updated_at,
    } == expected_db_team
