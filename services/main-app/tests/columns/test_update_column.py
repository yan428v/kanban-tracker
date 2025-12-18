import uuid

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from models import Board, BoardColumn, User


@pytest.mark.asyncio(loop_scope="session")
async def test_update_column_not_found(default_auth_client: AsyncClient):
    """Обновление несуществующей колонки должно вернуть 404."""
    non_existent_id = uuid.uuid4()
    response = await default_auth_client.patch(
        f"/api/v1/columns/{non_existent_id}", json={"title": "Updated Title"}
    )
    assert response.status_code == 404
    assert response.json() == {"detail": "Column not found"}


@pytest.mark.asyncio(loop_scope="session")
async def test_update_column_no_updates(
    default_auth_client: AsyncClient,
    default_auth_user: User,
    db_session: AsyncSession,
):
    """Обновление колонки без изменений должно вернуть 200."""
    board = Board(title="Test Board", owner_id=default_auth_user.id)
    db_session.add(board)
    await db_session.commit()
    await db_session.refresh(board)

    column = BoardColumn(title="Original Title", position=2, board_id=board.id)
    db_session.add(column)
    await db_session.commit()
    await db_session.refresh(column)

    original_created_at = column.created_at

    response = await default_auth_client.patch(f"/api/v1/columns/{column.id}", json={})
    assert response.status_code == 200
    data = response.json()

    await db_session.refresh(column)

    expected_response = {
        "id": str(column.id),
        "title": column.title,
        "position": column.position,
        "limit": column.limit,
        "board_id": str(column.board_id),
        "created_at": column.created_at.isoformat(),
        "updated_at": column.updated_at.isoformat(),
    }
    assert data == expected_response

    assert column.title == "Original Title"
    assert column.position == 2
    assert column.created_at == original_created_at


@pytest.mark.asyncio(loop_scope="session")
async def test_update_column_title_only(
    default_auth_client: AsyncClient,
    default_auth_user: User,
    db_session: AsyncSession,
):
    """Обновление только title колонки."""
    board = Board(title="Test Board", owner_id=default_auth_user.id)
    db_session.add(board)
    await db_session.commit()
    await db_session.refresh(board)

    column = BoardColumn(title="Original Title", position=2, board_id=board.id)
    db_session.add(column)
    await db_session.commit()
    await db_session.refresh(column)

    original_created_at = column.created_at

    response = await default_auth_client.patch(
        f"/api/v1/columns/{column.id}", json={"title": "Updated Title"}
    )
    assert response.status_code == 200
    data = response.json()

    await db_session.refresh(column)

    expected_response = {
        "id": str(column.id),
        "title": column.title,
        "position": column.position,
        "limit": column.limit,
        "board_id": str(column.board_id),
        "created_at": column.created_at.isoformat(),
        "updated_at": column.updated_at.isoformat(),
    }
    assert data == expected_response

    expected_db_column = {
        "id": column.id,
        "title": "Updated Title",
        "position": 2,
        "created_at": original_created_at,
        "updated_at": column.updated_at,
    }
    assert {
        "id": column.id,
        "title": column.title,
        "position": column.position,
        "created_at": column.created_at,
        "updated_at": column.updated_at,
    } == expected_db_column


@pytest.mark.asyncio(loop_scope="session")
async def test_update_column_position_only(
    default_auth_client: AsyncClient,
    default_auth_user: User,
    db_session: AsyncSession,
):
    """Обновление только position колонки."""
    board = Board(title="Test Board", owner_id=default_auth_user.id)
    db_session.add(board)
    await db_session.commit()
    await db_session.refresh(board)

    column = BoardColumn(title="Original Title", position=2, board_id=board.id)
    db_session.add(column)
    await db_session.commit()
    await db_session.refresh(column)

    original_created_at = column.created_at

    response = await default_auth_client.patch(
        f"/api/v1/columns/{column.id}", json={"position": 5}
    )
    assert response.status_code == 200
    data = response.json()

    await db_session.refresh(column)

    expected_response = {
        "id": str(column.id),
        "title": column.title,
        "position": column.position,
        "limit": column.limit,
        "board_id": str(column.board_id),
        "created_at": column.created_at.isoformat(),
        "updated_at": column.updated_at.isoformat(),
    }
    assert data == expected_response

    expected_db_column = {
        "id": column.id,
        "title": "Original Title",
        "position": 5,
        "created_at": original_created_at,
        "updated_at": column.updated_at,
    }
    assert {
        "id": column.id,
        "title": column.title,
        "position": column.position,
        "created_at": column.created_at,
        "updated_at": column.updated_at,
    } == expected_db_column


@pytest.mark.asyncio(loop_scope="session")
async def test_update_column_limit(
    default_auth_client: AsyncClient,
    default_auth_user: User,
    db_session: AsyncSession,
):
    """Обновление limit колонки."""
    board = Board(title="Test Board", owner_id=default_auth_user.id)
    db_session.add(board)
    await db_session.commit()
    await db_session.refresh(board)

    column = BoardColumn(title="Original Title", position=2, board_id=board.id)
    db_session.add(column)
    await db_session.commit()
    await db_session.refresh(column)

    response = await default_auth_client.patch(
        f"/api/v1/columns/{column.id}", json={"limit": 10}
    )
    assert response.status_code == 200

    await db_session.refresh(column)
    assert column.limit == 10


@pytest.mark.asyncio(loop_scope="session")
async def test_update_column_multiple_fields(
    default_auth_client: AsyncClient,
    default_auth_user: User,
    db_session: AsyncSession,
):
    """Обновление нескольких полей одновременно."""
    board = Board(title="Test Board", owner_id=default_auth_user.id)
    db_session.add(board)
    await db_session.commit()
    await db_session.refresh(board)

    column = BoardColumn(title="Original Title", position=2, board_id=board.id)
    db_session.add(column)
    await db_session.commit()
    await db_session.refresh(column)

    original_created_at = column.created_at

    response = await default_auth_client.patch(
        f"/api/v1/columns/{column.id}",
        json={"title": "Updated Title", "position": 7, "limit": 15},
    )
    assert response.status_code == 200
    data = response.json()

    await db_session.refresh(column)

    expected_response = {
        "id": str(column.id),
        "title": column.title,
        "position": column.position,
        "limit": column.limit,
        "board_id": str(column.board_id),
        "created_at": column.created_at.isoformat(),
        "updated_at": column.updated_at.isoformat(),
    }
    assert data == expected_response

    expected_db_column = {
        "id": column.id,
        "title": "Updated Title",
        "position": 7,
        "limit": 15,
        "created_at": original_created_at,
        "updated_at": column.updated_at,
    }
    assert {
        "id": column.id,
        "title": column.title,
        "position": column.position,
        "limit": column.limit,
        "created_at": column.created_at,
        "updated_at": column.updated_at,
    } == expected_db_column
