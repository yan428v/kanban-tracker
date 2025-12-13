import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from auth.security import hash_password
from models import Team, TeamMember, User


@pytest.fixture
async def seeded_team_members_data(db_session: AsyncSession):
    team = Team(name="Team 1")
    db_session.add(team)
    await db_session.commit()
    await db_session.refresh(team)

    hashed_password = hash_password("password")
    users = [
        User(
            name=f"User {i}",
            email=f"user{i}@example.com",
            hashed_password=hashed_password,
        )
        for i in range(1010)
    ]
    db_session.add_all(users)
    await db_session.commit()

    members = [TeamMember(team_id=team.id, user_id=user.id) for user in users]
    db_session.add_all(members)
    await db_session.commit()

    return {
        "team": team,
        "users": users,
        "members": members,
    }


@pytest.mark.asyncio(loop_scope="session")
async def test_no_team_members(test_client: AsyncClient):
    response = await test_client.get("/api/v1/team-members")
    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.asyncio(loop_scope="session")
async def test_two_team_members_no_params(
    test_client: AsyncClient, seeded_team_members_data
):
    members = seeded_team_members_data["members"]
    member1 = members[0]
    member2 = members[1]

    response = await test_client.get("/api/v1/team-members")
    assert response.status_code == 200
    data = response.json()

    assert len(data) == 100
    expected = [
        {
            "id": str(member1.id),
            "team_id": str(member1.team_id),
            "user_id": str(member1.user_id),
            "created_at": member1.created_at.isoformat(),
            "updated_at": member1.updated_at.isoformat(),
        },
        {
            "id": str(member2.id),
            "team_id": str(member2.team_id),
            "user_id": str(member2.user_id),
            "created_at": member2.created_at.isoformat(),
            "updated_at": member2.updated_at.isoformat(),
        },
    ]
    assert data[:2] == expected


@pytest.mark.asyncio(loop_scope="session")
async def test_skip_10(test_client: AsyncClient, seeded_team_members_data):
    response = await test_client.get("/api/v1/team-members?skip=15")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 100


@pytest.mark.asyncio(loop_scope="session")
async def test_limit_1(test_client: AsyncClient, seeded_team_members_data):
    members = seeded_team_members_data["members"]
    member1 = members[0]

    response = await test_client.get("/api/v1/team-members?limit=1")
    assert response.status_code == 200
    data = response.json()

    expected = [
        {
            "id": str(member1.id),
            "team_id": str(member1.team_id),
            "user_id": str(member1.user_id),
            "created_at": member1.created_at.isoformat(),
            "updated_at": member1.updated_at.isoformat(),
        }
    ]
    assert data == expected


@pytest.mark.asyncio(loop_scope="session")
async def test_limit_0(test_client: AsyncClient, seeded_team_members_data):
    response = await test_client.get("/api/v1/team-members?limit=0")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 100


@pytest.mark.asyncio(loop_scope="session")
async def test_limit_1001(test_client: AsyncClient, seeded_team_members_data):
    response = await test_client.get("/api/v1/team-members?limit=1001")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1000


@pytest.mark.asyncio(loop_scope="session")
async def test_skip_0(test_client: AsyncClient, seeded_team_members_data):
    members = seeded_team_members_data["members"]
    member1 = members[0]
    member2 = members[1]

    response = await test_client.get("/api/v1/team-members?skip=0")
    assert response.status_code == 200
    data = response.json()

    expected = [
        {
            "id": str(member1.id),
            "team_id": str(member1.team_id),
            "user_id": str(member1.user_id),
            "created_at": member1.created_at.isoformat(),
            "updated_at": member1.updated_at.isoformat(),
        },
        {
            "id": str(member2.id),
            "team_id": str(member2.team_id),
            "user_id": str(member2.user_id),
            "created_at": member2.created_at.isoformat(),
            "updated_at": member2.updated_at.isoformat(),
        },
    ]
    assert data[:2] == expected


@pytest.mark.asyncio(loop_scope="session")
async def test_skip_negative(test_client: AsyncClient, seeded_team_members_data):
    members = seeded_team_members_data["members"]
    member1 = members[0]
    member2 = members[1]

    response = await test_client.get("/api/v1/team-members?skip=-1")
    assert response.status_code == 200
    data = response.json()

    expected = [
        {
            "id": str(member1.id),
            "team_id": str(member1.team_id),
            "user_id": str(member1.user_id),
            "created_at": member1.created_at.isoformat(),
            "updated_at": member1.updated_at.isoformat(),
        },
        {
            "id": str(member2.id),
            "team_id": str(member2.team_id),
            "user_id": str(member2.user_id),
            "created_at": member2.created_at.isoformat(),
            "updated_at": member2.updated_at.isoformat(),
        },
    ]
    assert data[:2] == expected
