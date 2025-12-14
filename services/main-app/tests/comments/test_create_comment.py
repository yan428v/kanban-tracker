import uuid

import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models import Board, BoardColumn, Comment, Task, User


@pytest.fixture
async def test_data(db_session: AsyncSession):
    user = User(
        name="Test User",
        email="test@example.com",
        hashed_password="$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",
    )
    db_session.add(user)
    await db_session.flush()

    board = Board(title="Test Board", owner_id=user.id)
    db_session.add(board)
    await db_session.flush()

    column = BoardColumn(title="Test Column", board_id=board.id, position=0)
    db_session.add(column)
    await db_session.flush()

    task = Task(title="Test Task", user_id=user.id, column_id=column.id)
    db_session.add(task)
    await db_session.commit()
    await db_session.refresh(task)

    return {"user": user, "task": task}


@pytest.mark.asyncio(loop_scope="session")
async def test_create_comment_success(
    test_client: AsyncClient, test_data, db_session: AsyncSession
):
    user = test_data["user"]
    task = test_data["task"]

    payload = {
        "body": "New Comment",
        "user_id": str(user.id),
        "task_id": str(task.id),
    }

    response = await test_client.post("/api/v1/comments/", json=payload)
    assert response.status_code == 201
    data = response.json()

    comment_id = uuid.UUID(data["id"])
    result = await db_session.execute(select(Comment).where(Comment.id == comment_id))
    comment_in_db = result.scalar_one()

    expected_response = {
        "id": str(comment_in_db.id),
        "body": comment_in_db.body,
        "user_id": str(comment_in_db.user_id),
        "task_id": str(comment_in_db.task_id),
        "created_at": comment_in_db.created_at.isoformat(),
        "updated_at": comment_in_db.updated_at.isoformat(),
    }
    assert data == expected_response

    assert comment_in_db.body == "New Comment"
    assert comment_in_db.user_id == user.id
    assert comment_in_db.task_id == task.id


@pytest.mark.asyncio(loop_scope="session")
async def test_create_comment_missing_body(test_client: AsyncClient, test_data):
    user = test_data["user"]
    task = test_data["task"]

    payload = {
        "user_id": str(user.id),
        "task_id": str(task.id),
    }

    response = await test_client.post("/api/v1/comments/", json=payload)
    assert response.status_code == 422
    data = response.json()
    assert "detail" in data
    assert any(error.get("loc") == ["body", "body"] for error in data["detail"])


@pytest.mark.asyncio(loop_scope="session")
async def test_create_comment_missing_user_id(test_client: AsyncClient, test_data):
    task = test_data["task"]

    payload = {
        "body": "Test Comment",
        "task_id": str(task.id),
    }

    response = await test_client.post("/api/v1/comments/", json=payload)
    assert response.status_code == 422
    data = response.json()
    assert "detail" in data
    assert any(error.get("loc") == ["body", "user_id"] for error in data["detail"])


@pytest.mark.asyncio(loop_scope="session")
async def test_create_comment_missing_task_id(test_client: AsyncClient, test_data):
    user = test_data["user"]

    payload = {
        "body": "Test Comment",
        "user_id": str(user.id),
    }

    response = await test_client.post("/api/v1/comments/", json=payload)
    assert response.status_code == 422
    data = response.json()
    assert "detail" in data
    assert any(error.get("loc") == ["body", "task_id"] for error in data["detail"])


@pytest.mark.asyncio(loop_scope="session")
async def test_create_comment_empty_body(test_client: AsyncClient, test_data):
    user = test_data["user"]
    task = test_data["task"]

    payload = {
        "body": "",
        "user_id": str(user.id),
        "task_id": str(task.id),
    }

    response = await test_client.post("/api/v1/comments/", json=payload)
    assert response.status_code == 422
    data = response.json()
    assert "detail" in data


@pytest.mark.asyncio(loop_scope="session")
async def test_create_comment_nonexistent_user_id(test_client: AsyncClient, test_data):
    task = test_data["task"]
    nonexistent_user_id = uuid.uuid4()

    payload = {
        "body": "Test Comment",
        "user_id": str(nonexistent_user_id),
        "task_id": str(task.id),
    }

    response = await test_client.post("/api/v1/comments/", json=payload)
    assert response.status_code == 422


@pytest.mark.asyncio(loop_scope="session")
async def test_create_comment_nonexistent_task_id(test_client: AsyncClient, test_data):
    user = test_data["user"]
    nonexistent_task_id = uuid.uuid4()

    payload = {
        "body": "Test Comment",
        "user_id": str(user.id),
        "task_id": str(nonexistent_task_id),
    }

    response = await test_client.post("/api/v1/comments/", json=payload)
    assert response.status_code == 422


@pytest.mark.asyncio(loop_scope="session")
async def test_create_comment_invalid_uuid_format(test_client: AsyncClient):
    payload = {
        "body": "Test Comment",
        "user_id": "invalid-uuid",
        "task_id": "invalid-uuid",
    }

    response = await test_client.post("/api/v1/comments/", json=payload)
    assert response.status_code == 422
