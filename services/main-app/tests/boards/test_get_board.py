import uuid

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from models import Board, User


@pytest.mark.asyncio(loop_scope="session")
async def test_get_board_success(
    default_auth_client: AsyncClient,
    default_auth_user: User,
    db_session: AsyncSession,
):
    """Успешное получение доски по ID."""
    board = Board(
        title="Test Board",
        description="Test Description",
        is_public=True,
        owner_id=default_auth_user.id,
    )
    db_session.add(board)
    await db_session.commit()
    await db_session.refresh(board)

    response = await default_auth_client.get(f"/api/v1/boards/{board.id}")
    assert response.status_code == 200
    data = response.json()

    expected = {
        "id": str(board.id),
        "title": board.title,
        "description": board.description,
        "is_public": board.is_public,
        "owner_id": str(board.owner_id),
        "team_id": str(board.team_id) if board.team_id else None,
        "created_at": board.created_at.isoformat(),
        "updated_at": board.updated_at.isoformat(),
    }
    assert data == expected


@pytest.mark.asyncio(loop_scope="session")
async def test_get_board_not_found(default_auth_client: AsyncClient):
    """Получение несуществующей доски должно вернуть 404."""
    non_existent_id = uuid.uuid4()
    response = await default_auth_client.get(f"/api/v1/boards/{non_existent_id}")
    assert response.status_code == 404
    assert response.json() == {"detail": "Board not found"}
