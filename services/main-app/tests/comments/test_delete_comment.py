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

    comment = Comment(body="Comment to Delete", user_id=user.id, task_id=task.id)
    db_session.add(comment)
    await db_session.commit()
    await db_session.refresh(comment)

    return {"comment": comment, "user": user, "task": task}


@pytest.mark.asyncio(loop_scope="session")
async def test_delete_comment_success(
    test_client: AsyncClient, comment_data, db_session: AsyncSession
):
    comment = comment_data["comment"]
    comment_id = comment.id

    response = await test_client.delete(f"/api/v1/comments/{comment_id}")
    assert response.status_code == 204

    result = await db_session.execute(select(Comment).where(Comment.id == comment_id))
    comment_in_db = result.scalar_one_or_none()
    assert comment_in_db is None


@pytest.mark.asyncio(loop_scope="session")
async def test_delete_comment_not_found(test_client: AsyncClient):
    nonexistent_id = uuid.uuid4()

    response = await test_client.delete(f"/api/v1/comments/{nonexistent_id}")
    assert response.status_code == 404
    data = response.json()
    assert data == {"detail": "Comment not found"}


@pytest.mark.asyncio(loop_scope="session")
async def test_delete_comment_invalid_uuid(test_client: AsyncClient):
    response = await test_client.delete("/api/v1/comments/invalid-uuid")
    assert response.status_code == 422


@pytest.mark.asyncio(loop_scope="session")
async def test_delete_comment_twice(
    test_client: AsyncClient, comment_data, db_session: AsyncSession
):
    comment = comment_data["comment"]
    comment_id = comment.id

    response1 = await test_client.delete(f"/api/v1/comments/{comment_id}")
    assert response1.status_code == 204

    response2 = await test_client.delete(f"/api/v1/comments/{comment_id}")
    assert response2.status_code == 404
