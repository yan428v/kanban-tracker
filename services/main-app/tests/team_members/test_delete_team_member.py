import uuid

import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from auth.security import hash_password
from models import Team, TeamMember, User


@pytest.mark.asyncio(loop_scope="session")
async def test_delete_team_member_no_team_id(default_auth_client: AsyncClient):
    user_id = str(uuid.uuid4())
    response = await default_auth_client.request(
        method="DELETE", url="/api/v1/team-members", json={"user_id": user_id}
    )
    assert response.status_code == 400
    data = response.json()
    assert data == {"detail": "team_id is required"}


@pytest.mark.asyncio(loop_scope="session")
async def test_delete_team_member_no_user_id(default_auth_client: AsyncClient):
    team_id = str(uuid.uuid4())
    response = await default_auth_client.request(
        method="DELETE", url="/api/v1/team-members", json={"team_id": team_id}
    )
    assert response.status_code == 400
    data = response.json()
    assert data == {"detail": "user_id is required"}


@pytest.mark.asyncio(loop_scope="session")
async def test_delete_team_member_not_found(default_auth_client: AsyncClient):
    team_id = uuid.uuid4()
    user_id = uuid.uuid4()
    response = await default_auth_client.request(
        method="DELETE",
        url="/api/v1/team-members",
        json={"team_id": str(team_id), "user_id": str(user_id)},
    )
    assert response.status_code == 200


@pytest.mark.asyncio(loop_scope="session")
async def test_delete_team_member_success(
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

    team_id = team_member.team_id
    user_id = team_member.user_id

    response = await default_auth_client.request(
        method="DELETE",
        url="/api/v1/team-members",
        json={"team_id": str(team_id), "user_id": str(user_id)},
    )
    assert response.status_code == 200

    result = await db_session.execute(
        select(TeamMember).where(
            TeamMember.team_id == team_id, TeamMember.user_id == user_id
        )
    )
    team_member_in_db = result.scalar_one_or_none()
    assert team_member_in_db is None
