import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from models import Board, BoardColumn, Comment, Task, User


@pytest.fixture
async def seeded_comments_data(db_session: AsyncSession):
    user1 = User(
        name="User 1",
        email="user1@example.com",
        hashed_password="$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",
    )
    user2 = User(
        name="User 2",
        email="user2@example.com",
        hashed_password="$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",
    )
    db_session.add_all([user1, user2])
    await db_session.flush()

    board = Board(title="Test Board", owner_id=user1.id)
    db_session.add(board)
    await db_session.flush()

    column = BoardColumn(title="Test Column", board_id=board.id, position=0)
    db_session.add(column)
    await db_session.flush()

    task1 = Task(title="Task 1", user_id=user1.id, column_id=column.id)
    task2 = Task(title="Task 2", user_id=user1.id, column_id=column.id)
    db_session.add_all([task1, task2])
    await db_session.flush()

    comments = [
        Comment(body="Comment 1", user_id=user1.id, task_id=task1.id),
        Comment(body="Comment 2", user_id=user1.id, task_id=task1.id),
        Comment(body="Comment 3", user_id=user2.id, task_id=task1.id),
        Comment(body="Comment 4", user_id=user1.id, task_id=task2.id),
    ]
    db_session.add_all(comments)
    await db_session.commit()

    return {
        "users": [user1, user2],
        "tasks": [task1, task2],
        "comments": comments,
    }


@pytest.mark.asyncio(loop_scope="session")
async def test_list_comments_no_comments(test_client: AsyncClient):
    response = await test_client.get("/api/v1/comments/")
    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.asyncio(loop_scope="session")
async def test_list_comments_all(test_client: AsyncClient, seeded_comments_data):
    comments = seeded_comments_data["comments"]

    response = await test_client.get("/api/v1/comments/")
    assert response.status_code == 200
    data = response.json()

    assert len(data) == 4
    expected = [
        {
            "id": str(comment.id),
            "body": comment.body,
            "user_id": str(comment.user_id),
            "task_id": str(comment.task_id),
            "created_at": comment.created_at.isoformat(),
            "updated_at": comment.updated_at.isoformat(),
        }
        for comment in comments
    ]
    comment_ids = {comment["id"] for comment in data}
    expected_ids = {comment["id"] for comment in expected}
    assert comment_ids == expected_ids


@pytest.mark.asyncio(loop_scope="session")
async def test_list_comments_filter_by_task_id(
    test_client: AsyncClient, seeded_comments_data
):
    tasks = seeded_comments_data["tasks"]
    task1 = tasks[0]

    response = await test_client.get(f"/api/v1/comments/?task_id={task1.id}")
    assert response.status_code == 200
    data = response.json()

    assert len(data) == 3
    for comment in data:
        assert comment["task_id"] == str(task1.id)
        assert comment["body"] in ["Comment 1", "Comment 2", "Comment 3"]


@pytest.mark.asyncio(loop_scope="session")
async def test_list_comments_filter_by_user_id(
    test_client: AsyncClient, seeded_comments_data
):
    users = seeded_comments_data["users"]
    user1 = users[0]

    response = await test_client.get(f"/api/v1/comments/?user_id={user1.id}")
    assert response.status_code == 200
    data = response.json()

    assert len(data) == 3
    for comment in data:
        assert comment["user_id"] == str(user1.id)


@pytest.mark.asyncio(loop_scope="session")
async def test_list_comments_filter_by_task_and_user_id(
    test_client: AsyncClient, seeded_comments_data
):
    users = seeded_comments_data["users"]
    tasks = seeded_comments_data["tasks"]
    user1 = users[0]
    task1 = tasks[0]

    response = await test_client.get(
        f"/api/v1/comments/?task_id={task1.id}&user_id={user1.id}"
    )
    assert response.status_code == 200
    data = response.json()

    assert len(data) == 2
    for comment in data:
        assert comment["task_id"] == str(task1.id)
        assert comment["user_id"] == str(user1.id)
        assert comment["body"] in ["Comment 1", "Comment 2"]


@pytest.mark.asyncio(loop_scope="session")
async def test_list_comments_filter_no_results(
    test_client: AsyncClient, seeded_comments_data
):
    import uuid

    nonexistent_task_id = uuid.uuid4()
    response = await test_client.get(f"/api/v1/comments/?task_id={nonexistent_task_id}")
    assert response.status_code == 200
    data = response.json()
    assert data == []
