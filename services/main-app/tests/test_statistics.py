import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from src.models import Board, BoardColumn, Comment, Task, Team, User


@pytest.mark.asyncio(loop_scope="session")
async def test_entity_counts_no_data(test_client: AsyncClient):
    response = await test_client.get("/api/v1/statistics")
    assert response.status_code == 200

    data = response.json()
    assert data["entity_counts"] == {
        "teams": 0,
        "users": 0,
        "boards": 0,
        "tasks": 0,
        "comments": 0,
    }


@pytest.mark.asyncio(loop_scope="session")
async def test_entity_counts_multiple_entities(
    test_client: AsyncClient, db_session: AsyncSession
):
    users = [User(name="User", email=f"user{i}@example.com") for i in range(3)]
    for user in users:
        db_session.add(user)
    await db_session.flush()

    teams = [Team(name="Team") for _ in range(2)]
    for team in teams:
        db_session.add(team)
    await db_session.flush()

    boards = [Board(title="Board", owner_id=users[0].id) for _ in range(4)]
    for board in boards:
        db_session.add(board)
    await db_session.flush()

    columns = []
    for i, board in enumerate(boards):
        column = BoardColumn(title="Column", board_id=board.id, position=i)
        db_session.add(column)
        columns.append(column)
    await db_session.flush()

    tasks = []
    for column in columns:
        task = Task(title="Task", user_id=users[0].id, column_id=column.id)
        db_session.add(task)
        tasks.append(task)
    await db_session.flush()

    comments = [
        Comment(body="Comment", user_id=users[0].id, task_id=tasks[0].id)
        for _ in range(5)
    ]
    for comment in comments:
        db_session.add(comment)
    await db_session.commit()

    response = await test_client.get("/api/v1/statistics")
    assert response.status_code == 200

    data = response.json()
    counts = data["entity_counts"]

    assert counts["teams"] == 2
    assert counts["users"] == 3
    assert counts["boards"] == 4
    assert counts["tasks"] == 4
    assert counts["comments"] == 5
