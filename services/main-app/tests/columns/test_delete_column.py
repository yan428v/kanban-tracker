import uuid

import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models import Board, BoardColumn, User


@pytest.mark.asyncio(loop_scope="session")
async def test_delete_column_success(
    default_auth_client: AsyncClient,
    default_auth_user: User,
    db_session: AsyncSession,
):
    """Успешное удаление колонки."""
    board = Board(title="Test Board", owner_id=default_auth_user.id)
    db_session.add(board)
    await db_session.commit()
    await db_session.refresh(board)

    column = BoardColumn(title="To Delete", board_id=board.id)
    db_session.add(column)
    await db_session.commit()
    await db_session.refresh(column)

    column_id = column.id

    response = await default_auth_client.delete(f"/api/v1/columns/{column_id}")
    assert response.status_code == 204

    # Проверяем что колонка удалена из БД
    result = await db_session.execute(
        select(BoardColumn).where(BoardColumn.id == column_id)
    )
    column_in_db = result.scalar_one_or_none()
    assert column_in_db is None


@pytest.mark.asyncio(loop_scope="session")
async def test_delete_column_not_found(default_auth_client: AsyncClient):
    """Удаление несуществующей колонки должно вернуть 404."""
    non_existent_id = uuid.uuid4()
    response = await default_auth_client.delete(f"/api/v1/columns/{non_existent_id}")
    assert response.status_code == 404
    assert response.json() == {"detail": "Column not found"}
