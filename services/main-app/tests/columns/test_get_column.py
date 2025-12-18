import uuid

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from models import Board, BoardColumn, User


@pytest.mark.asyncio(loop_scope="session")
async def test_get_column_success(
    default_auth_client: AsyncClient,
    default_auth_user: User,
    db_session: AsyncSession,
):
    """Успешное получение колонки по ID."""
    board = Board(title="Test Board", owner_id=default_auth_user.id)
    db_session.add(board)
    await db_session.commit()
    await db_session.refresh(board)

    column = BoardColumn(title="Test Column", position=3, limit=5, board_id=board.id)
    db_session.add(column)
    await db_session.commit()
    await db_session.refresh(column)

    response = await default_auth_client.get(f"/api/v1/columns/{column.id}")
    assert response.status_code == 200
    data = response.json()

    expected = {
        "id": str(column.id),
        "title": column.title,
        "position": column.position,
        "limit": column.limit,
        "board_id": str(column.board_id),
        "created_at": column.created_at.isoformat(),
        "updated_at": column.updated_at.isoformat(),
    }
    assert data == expected


@pytest.mark.asyncio(loop_scope="session")
async def test_get_column_not_found(default_auth_client: AsyncClient):
    """Получение несуществующей колонки должно вернуть 404."""
    non_existent_id = uuid.uuid4()
    response = await default_auth_client.get(f"/api/v1/columns/{non_existent_id}")
    assert response.status_code == 404
    assert response.json() == {"detail": "Column not found"}
