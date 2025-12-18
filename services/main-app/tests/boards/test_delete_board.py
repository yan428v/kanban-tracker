import uuid

import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models import Board, User


@pytest.mark.asyncio(loop_scope="session")
async def test_delete_board_success(
    default_auth_client: AsyncClient,
    default_auth_user: User,
    db_session: AsyncSession,
):
    """Успешное удаление доски."""
    board = Board(title="To Delete", owner_id=default_auth_user.id)
    db_session.add(board)
    await db_session.commit()
    await db_session.refresh(board)

    board_id = board.id

    response = await default_auth_client.delete(f"/api/v1/boards/{board_id}")
    assert response.status_code == 204

    # Проверяем что доска удалена из БД
    result = await db_session.execute(select(Board).where(Board.id == board_id))
    board_in_db = result.scalar_one_or_none()
    assert board_in_db is None


@pytest.mark.asyncio(loop_scope="session")
async def test_delete_board_not_found(default_auth_client: AsyncClient):
    """Удаление несуществующей доски должно вернуть 404."""
    non_existent_id = uuid.uuid4()
    response = await default_auth_client.delete(f"/api/v1/boards/{non_existent_id}")
    assert response.status_code == 404
    assert response.json() == {"detail": "Board not found"}
