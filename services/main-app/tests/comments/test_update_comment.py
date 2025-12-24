import uuid

import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models import Board, BoardColumn, Comment, Task, User


@pytest.fixture
async def comment_data(db_session: AsyncSession):
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
    await db_session.flush()

    comment = Comment(body="Original Comment", user_id=user.id, task_id=task.id)
    db_session.add(comment)
    await db_session.commit()
    await db_session.refresh(comment)

    return {"comment": comment, "user": user, "task": task}


@pytest.mark.asyncio(loop_scope="session")
async def test_update_comment_success(
    test_client: AsyncClient, comment_data, db_session: AsyncSession
):
    comment = comment_data["comment"]
    original_created_at = comment.created_at

    payload = {"body": "Updated Comment"}

    response = await test_client.put(f"/api/v1/comments/{comment.id}", json=payload)
    assert response.status_code == 200
    data = response.json()

    await db_session.refresh(comment)
    result = await db_session.execute(select(Comment).where(Comment.id == comment.id))
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

    expected_db_comment = {
        "id": comment_in_db.id,
        "body": "Updated Comment",
        "user_id": comment_in_db.user_id,
        "task_id": comment_in_db.task_id,
        "created_at": original_created_at,
        "updated_at": comment_in_db.updated_at,
    }
    assert {
        "id": comment_in_db.id,
        "body": comment_in_db.body,
        "user_id": comment_in_db.user_id,
        "task_id": comment_in_db.task_id,
        "created_at": comment_in_db.created_at,
        "updated_at": comment_in_db.updated_at,
    } == expected_db_comment


@pytest.mark.asyncio(loop_scope="session")
async def test_update_comment_no_changes(
    test_client: AsyncClient, comment_data, db_session: AsyncSession
):
    comment = comment_data["comment"]
    original_body = comment.body
    original_created_at = comment.created_at

    payload = {}

    response = await test_client.put(f"/api/v1/comments/{comment.id}", json=payload)
    assert response.status_code == 200
    data = response.json()

    await db_session.refresh(comment)
    result = await db_session.execute(select(Comment).where(Comment.id == comment.id))
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

    expected_db_comment = {
        "id": comment_in_db.id,
        "body": original_body,
        "user_id": comment_in_db.user_id,
        "task_id": comment_in_db.task_id,
        "created_at": original_created_at,
        "updated_at": comment_in_db.updated_at,
    }
    assert {
        "id": comment_in_db.id,
        "body": comment_in_db.body,
        "user_id": comment_in_db.user_id,
        "task_id": comment_in_db.task_id,
        "created_at": comment_in_db.created_at,
        "updated_at": comment_in_db.updated_at,
    } == expected_db_comment


@pytest.mark.asyncio(loop_scope="session")
async def test_update_comment_not_found(test_client: AsyncClient):
    nonexistent_id = uuid.uuid4()
    payload = {"body": "Updated Comment"}

    response = await test_client.put(f"/api/v1/comments/{nonexistent_id}", json=payload)
    assert response.status_code == 404
    data = response.json()
    assert data == {"detail": "Comment not found"}


@pytest.mark.asyncio(loop_scope="session")
async def test_update_comment_empty_body(
    test_client: AsyncClient, comment_data, db_session: AsyncSession
):
    comment = comment_data["comment"]

    payload = {"body": ""}

    response = await test_client.put(f"/api/v1/comments/{comment.id}", json=payload)
    assert response.status_code == 422
    data = response.json()
    assert "detail" in data
    assert isinstance(data["detail"], list)


@pytest.mark.asyncio(loop_scope="session")
async def test_update_comment_invalid_uuid(test_client: AsyncClient):
    payload = {"body": "Updated Comment"}

    response = await test_client.put("/api/v1/comments/invalid-uuid", json=payload)
    assert response.status_code == 422
