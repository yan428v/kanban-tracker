import uuid

import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models import Board, BoardColumn, Task, User


@pytest.mark.asyncio(loop_scope="session")
async def test_delete_task_success(
    default_auth_client: AsyncClient,
    default_auth_user: User,
    db_session: AsyncSession,
):
    """Успешное удаление задачи."""
    board = Board(title="Test Board", owner_id=default_auth_user.id)
    db_session.add(board)
    await db_session.commit()
    await db_session.refresh(board)

    column = BoardColumn(title="Test Column", board_id=board.id)
    db_session.add(column)
    await db_session.commit()
    await db_session.refresh(column)

    task = Task(
        title="To Delete", user_id=default_auth_user.id, column_id=column.id
    )
    db_session.add(task)
    await db_session.commit()
    await db_session.refresh(task)

    task_id = task.id

    response = await default_auth_client.delete(f"/api/v1/tasks/{task_id}")
    assert response.status_code == 204

    # Проверяем что задача удалена из БД
    result = await db_session.execute(select(Task).where(Task.id == task_id))
    task_in_db = result.scalar_one_or_none()
    assert task_in_db is None


@pytest.mark.asyncio(loop_scope="session")
async def test_delete_task_not_found(default_auth_client: AsyncClient):
    """Удаление несуществующей задачи должно вернуть 404."""
    non_existent_id = uuid.uuid4()
    response = await default_auth_client.delete(f"/api/v1/tasks/{non_existent_id}")
    assert response.status_code == 404
    assert response.json() == {"detail": "Task not found"}
