import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from models import Team


@pytest.mark.asyncio(loop_scope="session")
async def test_no_teams(default_auth_client: AsyncClient):
    response = await default_auth_client.get("/api/v1/teams")
    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.asyncio(loop_scope="session")
async def test_two_teams_no_params(
    default_auth_client: AsyncClient, db_session: AsyncSession
):
    team1 = Team(name="Team 1")
    team2 = Team(name="Team 2")
    db_session.add(team1)
    db_session.add(team2)
    await db_session.commit()
    await db_session.refresh(team1)
    await db_session.refresh(team2)

    response = await default_auth_client.get("/api/v1/teams")
    assert response.status_code == 200
    data = response.json()

    expected = [
        {
            "id": str(team1.id),
            "name": team1.name,
            "description": team1.description,
            "created_at": team1.created_at.isoformat(),
            "updated_at": team1.updated_at.isoformat(),
        },
        {
            "id": str(team2.id),
            "name": team2.name,
            "description": team2.description,
            "created_at": team2.created_at.isoformat(),
            "updated_at": team2.updated_at.isoformat(),
        },
    ]
    assert data == expected


@pytest.mark.asyncio(loop_scope="session")
async def test_skip_10(default_auth_client: AsyncClient, db_session: AsyncSession):
    team1 = Team(name="Team 1")
    team2 = Team(name="Team 2")
    db_session.add(team1)
    db_session.add(team2)
    await db_session.commit()

    response = await default_auth_client.get("/api/v1/teams?skip=10")
    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.asyncio(loop_scope="session")
async def test_limit_1(default_auth_client: AsyncClient, db_session: AsyncSession):
    team1 = Team(name="Team 1")
    team2 = Team(name="Team 2")
    db_session.add(team1)
    db_session.add(team2)
    await db_session.commit()
    await db_session.refresh(team1)

    response = await default_auth_client.get("/api/v1/teams?limit=1")
    assert response.status_code == 200
    data = response.json()

    expected = [
        {
            "id": str(team1.id),
            "name": team1.name,
            "description": team1.description,
            "created_at": team1.created_at.isoformat(),
            "updated_at": team1.updated_at.isoformat(),
        }
    ]
    assert data == expected


@pytest.mark.asyncio(loop_scope="session")
async def test_limit_0(default_auth_client: AsyncClient, db_session: AsyncSession):
    team1 = Team(name="Team 1")
    team2 = Team(name="Team 2")
    db_session.add(team1)
    db_session.add(team2)
    await db_session.commit()

    response = await default_auth_client.get("/api/v1/teams?limit=0")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2


@pytest.mark.asyncio(loop_scope="session")
async def test_limit_1001(default_auth_client: AsyncClient, db_session: AsyncSession):
    teams = [Team(name=f"Team {i}") for i in range(1000)]
    for team in teams:
        db_session.add(team)
    await db_session.commit()

    response = await default_auth_client.get("/api/v1/teams?limit=1001")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1000


@pytest.mark.asyncio(loop_scope="session")
async def test_skip_0(default_auth_client: AsyncClient):
    response = await default_auth_client.get("/api/v1/teams?skip=0")
    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.asyncio(loop_scope="session")
async def test_skip_negative(
    default_auth_client: AsyncClient, db_session: AsyncSession
):
    team1 = Team(name="Team 1")
    team2 = Team(name="Team 2")
    db_session.add(team1)
    db_session.add(team2)
    await db_session.commit()
    await db_session.refresh(team1)
    await db_session.refresh(team2)

    response = await default_auth_client.get("/api/v1/teams?skip=-1")
    assert response.status_code == 200
    data = response.json()

    expected = [
        {
            "id": str(team1.id),
            "name": team1.name,
            "description": team1.description,
            "created_at": team1.created_at.isoformat(),
            "updated_at": team1.updated_at.isoformat(),
        },
        {
            "id": str(team2.id),
            "name": team2.name,
            "description": team2.description,
            "created_at": team2.created_at.isoformat(),
            "updated_at": team2.updated_at.isoformat(),
        },
    ]
    assert data == expected
