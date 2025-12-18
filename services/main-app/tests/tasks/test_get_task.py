import uuid
from datetime import datetime, timedelta

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from enums.task_status import TaskStatus
from models import Board, BoardColumn, Task, User


@pytest.mark.asyncio(loop_scope="session")
async def test_get_task_success(
    default_auth_client: AsyncClient,
    default_auth_user: User,
    db_session: AsyncSession,
):
    """Успешное получение задачи по ID."""
    board = Board(title="Test Board", owner_id=default_auth_user.id)
    db_session.add(board)
    await db_session.commit()
    await db_session.refresh(board)

    column = BoardColumn(title="Test Column", board_id=board.id)
    db_session.add(column)
    await db_session.commit()
    await db_session.refresh(column)

    due_date = datetime.utcnow() + timedelta(days=7)
    task = Task(
        title="Test Task",
        description="Test Description",
        status=TaskStatus.IN_PROGRESS,
        due_date=due_date,
        user_id=default_auth_user.id,
        column_id=column.id,
    )
    db_session.add(task)
    await db_session.commit()
    await db_session.refresh(task)

    response = await default_auth_client.get(f"/api/v1/tasks/{task.id}")
    assert response.status_code == 200
    data = response.json()

    expected = {
        "id": str(task.id),
        "title": task.title,
        "description": task.description,
        "status": task.status.value,
        "due_date": task.due_date.isoformat() if task.due_date else None,
        "user_id": str(task.user_id),
        "column_id": str(task.column_id),
        "created_at": task.created_at.isoformat(),
        "updated_at": task.updated_at.isoformat(),
    }
    assert data == expected


@pytest.mark.asyncio(loop_scope="session")
async def test_get_task_not_found(default_auth_client: AsyncClient):
    """Получение несуществующей задачи должно вернуть 404."""
    non_existent_id = uuid.uuid4()
    response = await default_auth_client.get(f"/api/v1/tasks/{non_existent_id}")
    assert response.status_code == 404
    assert response.json() == {"detail": "Task not found"}
