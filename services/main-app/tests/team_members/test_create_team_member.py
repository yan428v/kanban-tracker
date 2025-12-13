import uuid

import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from auth.security import hash_password
from models import Team, TeamMember, User


@pytest.mark.asyncio(loop_scope="session")
async def test_create_team_member_no_team_id(default_auth_client: AsyncClient):
    user_id = str(uuid.uuid4())
    response = await default_auth_client.post(
        "/api/v1/team-members", json={"user_id": user_id}
    )
    assert response.status_code == 422
    data = response.json()
    expected_response = {
        "detail": [
            {
                "type": "missing",
                "loc": ["body", "team_id"],
                "msg": "Field required",
                "input": {"user_id": user_id},
            }
        ]
    }
    assert data == expected_response


@pytest.mark.asyncio(loop_scope="session")
async def test_create_team_member_no_user_id(default_auth_client: AsyncClient):
    team_id = str(uuid.uuid4())
    response = await default_auth_client.post(
        "/api/v1/team-members", json={"team_id": team_id}
    )
    assert response.status_code == 422
    data = response.json()
    expected_response = {
        "detail": [
            {
                "type": "missing",
                "loc": ["body", "user_id"],
                "msg": "Field required",
                "input": {"team_id": team_id},
            }
        ]
    }
    assert data == expected_response


@pytest.mark.asyncio(loop_scope="session")
async def test_create_team_member_already_exists(
    default_auth_client: AsyncClient, db_session: AsyncSession
):
    team = Team(name="Test Team")
    db_session.add(team)
    await db_session.commit()
    await db_session.refresh(team)

    hashed_password = hash_password("password")
    user = User(
        name="Test User",
        email="test@example.com",
        hashed_password=hashed_password,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    team_member = TeamMember(team_id=team.id, user_id=user.id)
    db_session.add(team_member)
    await db_session.commit()
    await db_session.refresh(team_member)

    response = await default_auth_client.post(
        "/api/v1/team-members",
        json={"team_id": str(team.id), "user_id": str(user.id)},
    )
    assert response.status_code == 409
    data = response.json()
    assert data == {
        "detail": f"Team member with team_id {team.id} and user_id {user.id} already exists"
    }


@pytest.mark.asyncio(loop_scope="session")
async def test_create_team_member_nonexistent_team(
    default_auth_client: AsyncClient, db_session: AsyncSession
):
    hashed_password = hash_password("password")
    user = User(
        name="Test User",
        email="test@example.com",
        hashed_password=hashed_password,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    nonexistent_team_id = uuid.uuid4()
    response = await default_auth_client.post(
        "/api/v1/team-members",
        json={"team_id": str(nonexistent_team_id), "user_id": str(user.id)},
    )
    assert response.status_code == 404
    data = response.json()
    assert data == {"detail": f"Team {nonexistent_team_id} not found"}


@pytest.mark.asyncio(loop_scope="session")
async def test_create_team_member_nonexistent_user(
    default_auth_client: AsyncClient, db_session: AsyncSession
):
    team = Team(name="Test Team")
    db_session.add(team)
    await db_session.commit()
    await db_session.refresh(team)

    nonexistent_user_id = uuid.uuid4()
    response = await default_auth_client.post(
        "/api/v1/team-members",
        json={"team_id": str(team.id), "user_id": str(nonexistent_user_id)},
    )
    assert response.status_code == 404
    data = response.json()
    assert data == {"detail": f"User {nonexistent_user_id} not found"}


@pytest.mark.asyncio(loop_scope="session")
async def test_create_team_member_success(
    default_auth_client: AsyncClient, db_session: AsyncSession
):
    team = Team(name="Test Team")
    db_session.add(team)
    await db_session.commit()
    await db_session.refresh(team)

    hashed_password = hash_password("password")
    user = User(
        name="Test User",
        email="test@example.com",
        hashed_password=hashed_password,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    response = await default_auth_client.post(
        "/api/v1/team-members",
        json={"team_id": str(team.id), "user_id": str(user.id)},
    )
    assert response.status_code == 201
    data = response.json()

    team_member_id = uuid.UUID(data["id"])
    result = await db_session.execute(
        select(TeamMember).where(TeamMember.id == team_member_id)
    )
    team_member_in_db = result.scalar_one()

    expected_response = {
        "id": str(team_member_in_db.id),
        "team_id": str(team_member_in_db.team_id),
        "user_id": str(team_member_in_db.user_id),
        "created_at": team_member_in_db.created_at.isoformat(),
        "updated_at": team_member_in_db.updated_at.isoformat(),
    }
    assert data == expected_response
