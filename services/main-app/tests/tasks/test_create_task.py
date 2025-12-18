import uuid
from datetime import datetime, timedelta

import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from enums.task_status import TaskStatus
from models import Board, BoardColumn, Task, User


@pytest.mark.asyncio(loop_scope="session")
async def test_create_task_title_only(
    default_auth_client: AsyncClient,
    default_auth_user: User,
    db_session: AsyncSession,
):
    """Создание задачи только с обязательными полями."""
    board = Board(title="Test Board", owner_id=default_auth_user.id)
    db_session.add(board)
    await db_session.commit()
    await db_session.refresh(board)

    column = BoardColumn(title="Test Column", board_id=board.id)
    db_session.add(column)
    await db_session.commit()
    await db_session.refresh(column)

    response = await default_auth_client.post(
        "/api/v1/tasks",
        json={
            "title": "Test Task",
            "user_id": str(default_auth_user.id),
            "column_id": str(column.id),
        },
    )
    assert response.status_code == 201
    data = response.json()

    task_id = uuid.UUID(data["id"])
    result = await db_session.execute(select(Task).where(Task.id == task_id))
    task_in_db = result.scalar_one()

    expected_response = {
        "id": str(task_in_db.id),
        "title": task_in_db.title,
        "description": task_in_db.description,
        "status": task_in_db.status.value,
        "due_date": task_in_db.due_date.isoformat() if task_in_db.due_date else None,
        "user_id": str(task_in_db.user_id),
        "column_id": str(task_in_db.column_id),
        "created_at": task_in_db.created_at.isoformat(),
        "updated_at": task_in_db.updated_at.isoformat(),
    }
    assert data == expected_response

    assert task_in_db.title == "Test Task"
    assert task_in_db.description is None
    assert task_in_db.status == TaskStatus.PENDING
    assert task_in_db.due_date is None


@pytest.mark.asyncio(loop_scope="session")
async def test_create_task_with_all_fields(
    default_auth_client: AsyncClient,
    default_auth_user: User,
    db_session: AsyncSession,
):
    """Создание задачи со всеми полями."""
    board = Board(title="Test Board", owner_id=default_auth_user.id)
    db_session.add(board)
    await db_session.commit()
    await db_session.refresh(board)

    column = BoardColumn(title="Test Column", board_id=board.id)
    db_session.add(column)
    await db_session.commit()
    await db_session.refresh(column)

    due_date = datetime.utcnow() + timedelta(days=7)

    response = await default_auth_client.post(
        "/api/v1/tasks",
        json={
            "title": "Full Task",
            "description": "Task Description",
            "status": "IN_PROGRESS",
            "due_date": due_date.isoformat(),
            "user_id": str(default_auth_user.id),
            "column_id": str(column.id),
        },
    )
    assert response.status_code == 201
    data = response.json()

    task_id = uuid.UUID(data["id"])
    result = await db_session.execute(select(Task).where(Task.id == task_id))
    task_in_db = result.scalar_one()

    assert task_in_db.title == "Full Task"
    assert task_in_db.description == "Task Description"
    assert task_in_db.status == TaskStatus.IN_PROGRESS
    assert task_in_db.due_date is not None


@pytest.mark.asyncio(loop_scope="session")
async def test_create_task_no_title(
    default_auth_client: AsyncClient,
    default_auth_user: User,
    db_session: AsyncSession,
):
    """Создание задачи без title должно вернуть 422."""
    board = Board(title="Test Board", owner_id=default_auth_user.id)
    db_session.add(board)
    await db_session.commit()
    await db_session.refresh(board)

    column = BoardColumn(title="Test Column", board_id=board.id)
    db_session.add(column)
    await db_session.commit()
    await db_session.refresh(column)

    response = await default_auth_client.post(
        "/api/v1/tasks",
        json={
            "user_id": str(default_auth_user.id),
            "column_id": str(column.id),
        },
    )
    assert response.status_code == 422
    data = response.json()
    assert any(error["loc"] == ["body", "title"] for error in data["detail"])


@pytest.mark.asyncio(loop_scope="session")
async def test_create_task_no_user_id(
    default_auth_client: AsyncClient,
    default_auth_user: User,
    db_session: AsyncSession,
):
    """Создание задачи без user_id должно вернуть 422."""
    board = Board(title="Test Board", owner_id=default_auth_user.id)
    db_session.add(board)
    await db_session.commit()
    await db_session.refresh(board)

    column = BoardColumn(title="Test Column", board_id=board.id)
    db_session.add(column)
    await db_session.commit()
    await db_session.refresh(column)

    response = await default_auth_client.post(
        "/api/v1/tasks",
        json={
            "title": "Test Task",
            "column_id": str(column.id),
        },
    )
    assert response.status_code == 422
    data = response.json()
    assert any(error["loc"] == ["body", "user_id"] for error in data["detail"])


@pytest.mark.asyncio(loop_scope="session")
async def test_create_task_no_column_id(
    default_auth_client: AsyncClient, default_auth_user: User
):
    """Создание задачи без column_id должно вернуть 422."""
    response = await default_auth_client.post(
        "/api/v1/tasks",
        json={
            "title": "Test Task",
            "user_id": str(default_auth_user.id),
        },
    )
    assert response.status_code == 422
    data = response.json()
    assert any(error["loc"] == ["body", "column_id"] for error in data["detail"])


@pytest.mark.asyncio(loop_scope="session")
async def test_create_task_empty_body(default_auth_client: AsyncClient):
    """Создание задачи с пустым телом должно вернуть 422."""
    response = await default_auth_client.post("/api/v1/tasks", json={})
    assert response.status_code == 422
