import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from models import Board, BoardColumn, Task, User


@pytest.mark.asyncio(loop_scope="session")
async def test_no_tasks(default_auth_client: AsyncClient):
    """Получение пустого списка задач."""
    response = await default_auth_client.get("/api/v1/tasks")
    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.asyncio(loop_scope="session")
async def test_two_tasks_no_params(
    default_auth_client: AsyncClient,
    default_auth_user: User,
    db_session: AsyncSession,
):
    """Получение списка из двух задач."""
    board = Board(title="Test Board", owner_id=default_auth_user.id)
    db_session.add(board)
    await db_session.commit()
    await db_session.refresh(board)

    column = BoardColumn(title="Test Column", board_id=board.id)
    db_session.add(column)
    await db_session.commit()
    await db_session.refresh(column)

    task1 = Task(
        title="Task 1", user_id=default_auth_user.id, column_id=column.id
    )
    task2 = Task(
        title="Task 2", user_id=default_auth_user.id, column_id=column.id
    )
    db_session.add(task1)
    db_session.add(task2)
    await db_session.commit()
    await db_session.refresh(task1)
    await db_session.refresh(task2)

    response = await default_auth_client.get("/api/v1/tasks")
    assert response.status_code == 200
    data = response.json()

    expected = [
        {
            "id": str(task1.id),
            "title": task1.title,
            "description": task1.description,
            "status": task1.status.value,
            "due_date": task1.due_date.isoformat() if task1.due_date else None,
            "user_id": str(task1.user_id),
            "column_id": str(task1.column_id),
            "created_at": task1.created_at.isoformat(),
            "updated_at": task1.updated_at.isoformat(),
        },
        {
            "id": str(task2.id),
            "title": task2.title,
            "description": task2.description,
            "status": task2.status.value,
            "due_date": task2.due_date.isoformat() if task2.due_date else None,
            "user_id": str(task2.user_id),
            "column_id": str(task2.column_id),
            "created_at": task2.created_at.isoformat(),
            "updated_at": task2.updated_at.isoformat(),
        },
    ]
    assert data == expected


@pytest.mark.asyncio(loop_scope="session")
async def test_skip_10(
    default_auth_client: AsyncClient,
    default_auth_user: User,
    db_session: AsyncSession,
):
    """Пропуск 10 задач должен вернуть пустой список."""
    board = Board(title="Test Board", owner_id=default_auth_user.id)
    db_session.add(board)
    await db_session.commit()
    await db_session.refresh(board)

    column = BoardColumn(title="Test Column", board_id=board.id)
    db_session.add(column)
    await db_session.commit()
    await db_session.refresh(column)

    task1 = Task(
        title="Task 1", user_id=default_auth_user.id, column_id=column.id
    )
    task2 = Task(
        title="Task 2", user_id=default_auth_user.id, column_id=column.id
    )
    db_session.add(task1)
    db_session.add(task2)
    await db_session.commit()

    response = await default_auth_client.get("/api/v1/tasks?skip=10")
    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.asyncio(loop_scope="session")
async def test_limit_1(
    default_auth_client: AsyncClient,
    default_auth_user: User,
    db_session: AsyncSession,
):
    """Лимит 1 должен вернуть только первую задачу."""
    board = Board(title="Test Board", owner_id=default_auth_user.id)
    db_session.add(board)
    await db_session.commit()
    await db_session.refresh(board)

    column = BoardColumn(title="Test Column", board_id=board.id)
    db_session.add(column)
    await db_session.commit()
    await db_session.refresh(column)

    task1 = Task(
        title="Task 1", user_id=default_auth_user.id, column_id=column.id
    )
    task2 = Task(
        title="Task 2", user_id=default_auth_user.id, column_id=column.id
    )
    db_session.add(task1)
    db_session.add(task2)
    await db_session.commit()
    await db_session.refresh(task1)

    response = await default_auth_client.get("/api/v1/tasks?limit=1")
    assert response.status_code == 200
    data = response.json()

    expected = [
        {
            "id": str(task1.id),
            "title": task1.title,
            "description": task1.description,
            "status": task1.status.value,
            "due_date": task1.due_date.isoformat() if task1.due_date else None,
            "user_id": str(task1.user_id),
            "column_id": str(task1.column_id),
            "created_at": task1.created_at.isoformat(),
            "updated_at": task1.updated_at.isoformat(),
        }
    ]
    assert data == expected


@pytest.mark.asyncio(loop_scope="session")
async def test_skip_negative(
    default_auth_client: AsyncClient,
    default_auth_user: User,
    db_session: AsyncSession,
):
    """Отрицательный skip должен работать как 0."""
    board = Board(title="Test Board", owner_id=default_auth_user.id)
    db_session.add(board)
    await db_session.commit()
    await db_session.refresh(board)

    column = BoardColumn(title="Test Column", board_id=board.id)
    db_session.add(column)
    await db_session.commit()
    await db_session.refresh(column)

    task1 = Task(
        title="Task 1", user_id=default_auth_user.id, column_id=column.id
    )
    db_session.add(task1)
    await db_session.commit()
    await db_session.refresh(task1)

    response = await default_auth_client.get("/api/v1/tasks?skip=-1")
    assert response.status_code == 200
    data = response.json()

    expected = [
        {
            "id": str(task1.id),
            "title": task1.title,
            "description": task1.description,
            "status": task1.status.value,
            "due_date": task1.due_date.isoformat() if task1.due_date else None,
            "user_id": str(task1.user_id),
            "column_id": str(task1.column_id),
            "created_at": task1.created_at.isoformat(),
            "updated_at": task1.updated_at.isoformat(),
        }
    ]
    assert data == expected
