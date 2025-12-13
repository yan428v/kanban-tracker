import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from auth.security import hash_password
from models import Board, BoardColumn, Comment, Task, Team, User


@pytest.mark.asyncio(loop_scope="session")
async def test_entity_counts_no_data(
    default_auth_client: AsyncClient,
    db_session: AsyncSession,
    default_auth_user: User,
):
    response = await default_auth_client.get("/api/v1/statistics")
    assert response.status_code == 200

    data = response.json()
    assert data["entity_counts"] == {
        "teams": 0,
        "users": 1,
        "boards": 0,
        "tasks": 0,
        "comments": 0,
    }

    result = await db_session.execute(select(User))
    user = result.scalar_one()
    assert user.email == default_auth_user.email


@pytest.mark.asyncio(loop_scope="session")
async def test_entity_counts_multiple_entities(
    default_auth_client: AsyncClient, db_session: AsyncSession
):
    users = [
        User(
            name="User",
            email=f"user{i}@example.com",
            hashed_password=hash_password("password"),
        )
        for i in range(3)
    ]
    db_session.add_all(users)
    await db_session.flush()

    teams = [Team(name="Team") for _ in range(2)]
    db_session.add_all(teams)
    await db_session.flush()

    boards = [Board(title="Board", owner_id=users[0].id) for _ in range(4)]
    db_session.add_all(boards)
    await db_session.flush()

    columns = [
        BoardColumn(title="Column", board_id=board.id, position=i)
        for i, board in enumerate(boards)
    ]
    db_session.add_all(columns)
    await db_session.flush()

    tasks = [
        Task(title="Task", user_id=users[0].id, column_id=column.id)
        for column in columns
    ]
    db_session.add_all(tasks)
    await db_session.flush()

    comments = [
        Comment(body="Comment", user_id=users[0].id, task_id=tasks[0].id)
        for _ in range(5)
    ]
    db_session.add_all(comments)
    await db_session.commit()

    response = await default_auth_client.get("/api/v1/statistics")
    assert response.status_code == 200

    data = response.json()
    counts = data["entity_counts"]

    assert counts["teams"] == 2
    assert counts["users"] == 4
    assert counts["boards"] == 4
    assert counts["tasks"] == 4
    assert counts["comments"] == 5
