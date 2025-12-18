import uuid

import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models import Board, BoardColumn, User


@pytest.mark.asyncio(loop_scope="session")
async def test_create_column_title_only(
    default_auth_client: AsyncClient,
    default_auth_user: User,
    db_session: AsyncSession,
):
    """Создание колонки только с обязательными полями."""
    board = Board(title="Test Board", owner_id=default_auth_user.id)
    db_session.add(board)
    await db_session.commit()
    await db_session.refresh(board)

    response = await default_auth_client.post(
        "/api/v1/columns", json={"title": "Test Column", "board_id": str(board.id)}
    )
    assert response.status_code == 201
    data = response.json()

    column_id = uuid.UUID(data["id"])
    result = await db_session.execute(
        select(BoardColumn).where(BoardColumn.id == column_id)
    )
    column_in_db = result.scalar_one()

    expected_response = {
        "id": str(column_in_db.id),
        "title": column_in_db.title,
        "position": column_in_db.position,
        "limit": column_in_db.limit,
        "board_id": str(column_in_db.board_id),
        "created_at": column_in_db.created_at.isoformat(),
        "updated_at": column_in_db.updated_at.isoformat(),
    }
    assert data == expected_response

    assert column_in_db.title == "Test Column"
    assert column_in_db.position == 0
    assert column_in_db.limit is None


@pytest.mark.asyncio(loop_scope="session")
async def test_create_column_with_all_fields(
    default_auth_client: AsyncClient,
    default_auth_user: User,
    db_session: AsyncSession,
):
    """Создание колонки со всеми полями."""
    board = Board(title="Test Board", owner_id=default_auth_user.id)
    db_session.add(board)
    await db_session.commit()
    await db_session.refresh(board)

    response = await default_auth_client.post(
        "/api/v1/columns",
        json={
            "title": "Full Column",
            "position": 5,
            "limit": 10,
            "board_id": str(board.id),
        },
    )
    assert response.status_code == 201
    data = response.json()

    column_id = uuid.UUID(data["id"])
    result = await db_session.execute(
        select(BoardColumn).where(BoardColumn.id == column_id)
    )
    column_in_db = result.scalar_one()

    assert column_in_db.title == "Full Column"
    assert column_in_db.position == 5
    assert column_in_db.limit == 10


@pytest.mark.asyncio(loop_scope="session")
async def test_create_column_no_title(
    default_auth_client: AsyncClient,
    default_auth_user: User,
    db_session: AsyncSession,
):
    """Создание колонки без title должно вернуть 422."""
    board = Board(title="Test Board", owner_id=default_auth_user.id)
    db_session.add(board)
    await db_session.commit()
    await db_session.refresh(board)

    response = await default_auth_client.post(
        "/api/v1/columns", json={"board_id": str(board.id)}
    )
    assert response.status_code == 422
    data = response.json()
    assert any(error["loc"] == ["body", "title"] for error in data["detail"])


@pytest.mark.asyncio(loop_scope="session")
async def test_create_column_no_board_id(default_auth_client: AsyncClient):
    """Создание колонки без board_id должно вернуть 422."""
    response = await default_auth_client.post(
        "/api/v1/columns", json={"title": "Test Column"}
    )
    assert response.status_code == 422
    data = response.json()
    assert any(error["loc"] == ["body", "board_id"] for error in data["detail"])


@pytest.mark.asyncio(loop_scope="session")
async def test_create_column_empty_body(default_auth_client: AsyncClient):
    """Создание колонки с пустым телом должно вернуть 422."""
    response = await default_auth_client.post("/api/v1/columns", json={})
    assert response.status_code == 422
