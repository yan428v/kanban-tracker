import uuid
from datetime import datetime, timedelta

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from enums.task_status import TaskStatus
from models import Board, BoardColumn, Task, User


@pytest.mark.asyncio(loop_scope="session")
async def test_update_task_not_found(default_auth_client: AsyncClient):
    """Обновление несуществующей задачи должно вернуть 404."""
    non_existent_id = uuid.uuid4()
    response = await default_auth_client.patch(
        f"/api/v1/tasks/{non_existent_id}", json={"title": "Updated Title"}
    )
    assert response.status_code == 404
    assert response.json() == {"detail": "Task not found"}


@pytest.mark.asyncio(loop_scope="session")
async def test_update_task_no_updates(
    default_auth_client: AsyncClient,
    default_auth_user: User,
    db_session: AsyncSession,
):
    """Обновление задачи без изменений должно вернуть 200."""
    board = Board(title="Test Board", owner_id=default_auth_user.id)
    db_session.add(board)
    await db_session.commit()
    await db_session.refresh(board)

    column = BoardColumn(title="Test Column", board_id=board.id)
    db_session.add(column)
    await db_session.commit()
    await db_session.refresh(column)

    task = Task(
        title="Original Title",
        description="Original Description",
        user_id=default_auth_user.id,
        column_id=column.id,
    )
    db_session.add(task)
    await db_session.commit()
    await db_session.refresh(task)

    original_created_at = task.created_at

    response = await default_auth_client.patch(f"/api/v1/tasks/{task.id}", json={})
    assert response.status_code == 200
    data = response.json()

    await db_session.refresh(task)

    expected_response = {
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
    assert data == expected_response

    assert task.title == "Original Title"
    assert task.description == "Original Description"
    assert task.created_at == original_created_at


@pytest.mark.asyncio(loop_scope="session")
async def test_update_task_title_only(
    default_auth_client: AsyncClient,
    default_auth_user: User,
    db_session: AsyncSession,
):
    """Обновление только title задачи."""
    board = Board(title="Test Board", owner_id=default_auth_user.id)
    db_session.add(board)
    await db_session.commit()
    await db_session.refresh(board)

    column = BoardColumn(title="Test Column", board_id=board.id)
    db_session.add(column)
    await db_session.commit()
    await db_session.refresh(column)

    task = Task(
        title="Original Title",
        description="Original Description",
        user_id=default_auth_user.id,
        column_id=column.id,
    )
    db_session.add(task)
    await db_session.commit()
    await db_session.refresh(task)

    original_created_at = task.created_at

    response = await default_auth_client.patch(
        f"/api/v1/tasks/{task.id}", json={"title": "Updated Title"}
    )
    assert response.status_code == 200
    data = response.json()

    await db_session.refresh(task)

    expected_response = {
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
    assert data == expected_response

    expected_db_task = {
        "id": task.id,
        "title": "Updated Title",
        "description": "Original Description",
        "created_at": original_created_at,
        "updated_at": task.updated_at,
    }
    assert {
        "id": task.id,
        "title": task.title,
        "description": task.description,
        "created_at": task.created_at,
        "updated_at": task.updated_at,
    } == expected_db_task


@pytest.mark.asyncio(loop_scope="session")
async def test_update_task_description_only(
    default_auth_client: AsyncClient,
    default_auth_user: User,
    db_session: AsyncSession,
):
    """Обновление только description задачи."""
    board = Board(title="Test Board", owner_id=default_auth_user.id)
    db_session.add(board)
    await db_session.commit()
    await db_session.refresh(board)

    column = BoardColumn(title="Test Column", board_id=board.id)
    db_session.add(column)
    await db_session.commit()
    await db_session.refresh(column)

    task = Task(
        title="Original Title",
        description="Original Description",
        user_id=default_auth_user.id,
        column_id=column.id,
    )
    db_session.add(task)
    await db_session.commit()
    await db_session.refresh(task)

    original_created_at = task.created_at

    response = await default_auth_client.patch(
        f"/api/v1/tasks/{task.id}", json={"description": "Updated Description"}
    )
    assert response.status_code == 200
    data = response.json()

    await db_session.refresh(task)

    expected_response = {
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
    assert data == expected_response

    expected_db_task = {
        "id": task.id,
        "title": "Original Title",
        "description": "Updated Description",
        "created_at": original_created_at,
        "updated_at": task.updated_at,
    }
    assert {
        "id": task.id,
        "title": task.title,
        "description": task.description,
        "created_at": task.created_at,
        "updated_at": task.updated_at,
    } == expected_db_task


@pytest.mark.asyncio(loop_scope="session")
async def test_update_task_status(
    default_auth_client: AsyncClient,
    default_auth_user: User,
    db_session: AsyncSession,
):
    """Обновление статуса задачи."""
    board = Board(title="Test Board", owner_id=default_auth_user.id)
    db_session.add(board)
    await db_session.commit()
    await db_session.refresh(board)

    column = BoardColumn(title="Test Column", board_id=board.id)
    db_session.add(column)
    await db_session.commit()
    await db_session.refresh(column)

    task = Task(
        title="Test Task",
        status=TaskStatus.PENDING,
        user_id=default_auth_user.id,
        column_id=column.id,
    )
    db_session.add(task)
    await db_session.commit()
    await db_session.refresh(task)

    response = await default_auth_client.patch(
        f"/api/v1/tasks/{task.id}", json={"status": "COMPLETED"}
    )
    assert response.status_code == 200

    await db_session.refresh(task)
    assert task.status == TaskStatus.COMPLETED


@pytest.mark.asyncio(loop_scope="session")
async def test_update_task_due_date(
    default_auth_client: AsyncClient,
    default_auth_user: User,
    db_session: AsyncSession,
):
    """Обновление due_date задачи."""
    board = Board(title="Test Board", owner_id=default_auth_user.id)
    db_session.add(board)
    await db_session.commit()
    await db_session.refresh(board)

    column = BoardColumn(title="Test Column", board_id=board.id)
    db_session.add(column)
    await db_session.commit()
    await db_session.refresh(column)

    task = Task(
        title="Test Task",
        user_id=default_auth_user.id,
        column_id=column.id,
    )
    db_session.add(task)
    await db_session.commit()
    await db_session.refresh(task)

    new_due_date = datetime.utcnow() + timedelta(days=14)

    response = await default_auth_client.patch(
        f"/api/v1/tasks/{task.id}", json={"due_date": new_due_date.isoformat()}
    )
    assert response.status_code == 200

    await db_session.refresh(task)
    assert task.due_date is not None


@pytest.mark.asyncio(loop_scope="session")
async def test_update_task_column_id(
    default_auth_client: AsyncClient,
    default_auth_user: User,
    db_session: AsyncSession,
):
    """Перемещение задачи в другую колонку."""
    board = Board(title="Test Board", owner_id=default_auth_user.id)
    db_session.add(board)
    await db_session.commit()
    await db_session.refresh(board)

    column1 = BoardColumn(title="Column 1", board_id=board.id)
    column2 = BoardColumn(title="Column 2", board_id=board.id)
    db_session.add(column1)
    db_session.add(column2)
    await db_session.commit()
    await db_session.refresh(column1)
    await db_session.refresh(column2)

    task = Task(
        title="Test Task",
        user_id=default_auth_user.id,
        column_id=column1.id,
    )
    db_session.add(task)
    await db_session.commit()
    await db_session.refresh(task)

    response = await default_auth_client.patch(
        f"/api/v1/tasks/{task.id}", json={"column_id": str(column2.id)}
    )
    assert response.status_code == 200

    await db_session.refresh(task)
    assert task.column_id == column2.id


@pytest.mark.asyncio(loop_scope="session")
async def test_update_task_multiple_fields(
    default_auth_client: AsyncClient,
    default_auth_user: User,
    db_session: AsyncSession,
):
    """Обновление нескольких полей одновременно."""
    board = Board(title="Test Board", owner_id=default_auth_user.id)
    db_session.add(board)
    await db_session.commit()
    await db_session.refresh(board)

    column1 = BoardColumn(title="Column 1", board_id=board.id)
    column2 = BoardColumn(title="Column 2", board_id=board.id)
    db_session.add(column1)
    db_session.add(column2)
    await db_session.commit()
    await db_session.refresh(column1)
    await db_session.refresh(column2)

    task = Task(
        title="Original Title",
        description="Original Description",
        status=TaskStatus.PENDING,
        user_id=default_auth_user.id,
        column_id=column1.id,
    )
    db_session.add(task)
    await db_session.commit()
    await db_session.refresh(task)

    original_created_at = task.created_at
    new_due_date = datetime.utcnow() + timedelta(days=7)

    response = await default_auth_client.patch(
        f"/api/v1/tasks/{task.id}",
        json={
            "title": "Updated Title",
            "description": "Updated Description",
            "status": "IN_PROGRESS",
            "due_date": new_due_date.isoformat(),
            "column_id": str(column2.id),
        },
    )
    assert response.status_code == 200
    data = response.json()

    await db_session.refresh(task)

    expected_response = {
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
    assert data == expected_response

    expected_db_task = {
        "id": task.id,
        "title": "Updated Title",
        "description": "Updated Description",
        "status": TaskStatus.IN_PROGRESS,
        "column_id": column2.id,
        "created_at": original_created_at,
        "updated_at": task.updated_at,
    }
    assert {
        "id": task.id,
        "title": task.title,
        "description": task.description,
        "status": task.status,
        "column_id": task.column_id,
        "created_at": task.created_at,
        "updated_at": task.updated_at,
    } == expected_db_task
