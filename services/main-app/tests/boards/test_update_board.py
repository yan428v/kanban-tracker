import uuid

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from models import Board, User


@pytest.mark.asyncio(loop_scope="session")
async def test_update_board_not_found(default_auth_client: AsyncClient):
    """Обновление несуществующей доски должно вернуть 404."""
    non_existent_id = uuid.uuid4()
    response = await default_auth_client.patch(
        f"/api/v1/boards/{non_existent_id}", json={"title": "Updated Title"}
    )
    assert response.status_code == 404
    assert response.json() == {"detail": "Board not found"}


@pytest.mark.asyncio(loop_scope="session")
async def test_update_board_no_updates(
    default_auth_client: AsyncClient,
    default_auth_user: User,
    db_session: AsyncSession,
):
    """Обновление доски без изменений должно вернуть 200."""
    board = Board(
        title="Original Title",
        description="Original Description",
        owner_id=default_auth_user.id,
    )
    db_session.add(board)
    await db_session.commit()
    await db_session.refresh(board)

    original_created_at = board.created_at

    response = await default_auth_client.patch(f"/api/v1/boards/{board.id}", json={})
    assert response.status_code == 200
    data = response.json()

    await db_session.refresh(board)

    expected_response = {
        "id": str(board.id),
        "title": board.title,
        "description": board.description,
        "is_public": board.is_public,
        "owner_id": str(board.owner_id),
        "team_id": str(board.team_id) if board.team_id else None,
        "created_at": board.created_at.isoformat(),
        "updated_at": board.updated_at.isoformat(),
    }
    assert data == expected_response

    assert board.title == "Original Title"
    assert board.description == "Original Description"
    assert board.created_at == original_created_at


@pytest.mark.asyncio(loop_scope="session")
async def test_update_board_title_only(
    default_auth_client: AsyncClient,
    default_auth_user: User,
    db_session: AsyncSession,
):
    """Обновление только title доски."""
    board = Board(
        title="Original Title",
        description="Original Description",
        owner_id=default_auth_user.id,
    )
    db_session.add(board)
    await db_session.commit()
    await db_session.refresh(board)

    original_created_at = board.created_at

    response = await default_auth_client.patch(
        f"/api/v1/boards/{board.id}", json={"title": "Updated Title"}
    )
    assert response.status_code == 200
    data = response.json()

    await db_session.refresh(board)

    expected_response = {
        "id": str(board.id),
        "title": board.title,
        "description": board.description,
        "is_public": board.is_public,
        "owner_id": str(board.owner_id),
        "team_id": str(board.team_id) if board.team_id else None,
        "created_at": board.created_at.isoformat(),
        "updated_at": board.updated_at.isoformat(),
    }
    assert data == expected_response

    expected_db_board = {
        "id": board.id,
        "title": "Updated Title",
        "description": "Original Description",
        "created_at": original_created_at,
        "updated_at": board.updated_at,
    }
    assert {
        "id": board.id,
        "title": board.title,
        "description": board.description,
        "created_at": board.created_at,
        "updated_at": board.updated_at,
    } == expected_db_board


@pytest.mark.asyncio(loop_scope="session")
async def test_update_board_description_only(
    default_auth_client: AsyncClient,
    default_auth_user: User,
    db_session: AsyncSession,
):
    """Обновление только description доски."""
    board = Board(
        title="Original Title",
        description="Original Description",
        owner_id=default_auth_user.id,
    )
    db_session.add(board)
    await db_session.commit()
    await db_session.refresh(board)

    original_created_at = board.created_at

    response = await default_auth_client.patch(
        f"/api/v1/boards/{board.id}", json={"description": "Updated Description"}
    )
    assert response.status_code == 200
    data = response.json()

    await db_session.refresh(board)

    expected_response = {
        "id": str(board.id),
        "title": board.title,
        "description": board.description,
        "is_public": board.is_public,
        "owner_id": str(board.owner_id),
        "team_id": str(board.team_id) if board.team_id else None,
        "created_at": board.created_at.isoformat(),
        "updated_at": board.updated_at.isoformat(),
    }
    assert data == expected_response

    expected_db_board = {
        "id": board.id,
        "title": "Original Title",
        "description": "Updated Description",
        "created_at": original_created_at,
        "updated_at": board.updated_at,
    }
    assert {
        "id": board.id,
        "title": board.title,
        "description": board.description,
        "created_at": board.created_at,
        "updated_at": board.updated_at,
    } == expected_db_board


@pytest.mark.asyncio(loop_scope="session")
async def test_update_board_is_public(
    default_auth_client: AsyncClient,
    default_auth_user: User,
    db_session: AsyncSession,
):
    """Обновление флага is_public."""
    board = Board(
        title="Original Title",
        description="Original Description",
        is_public=False,
        owner_id=default_auth_user.id,
    )
    db_session.add(board)
    await db_session.commit()
    await db_session.refresh(board)

    response = await default_auth_client.patch(
        f"/api/v1/boards/{board.id}", json={"is_public": True}
    )
    assert response.status_code == 200

    await db_session.refresh(board)
    assert board.is_public is True


@pytest.mark.asyncio(loop_scope="session")
async def test_update_board_multiple_fields(
    default_auth_client: AsyncClient,
    default_auth_user: User,
    db_session: AsyncSession,
):
    """Обновление нескольких полей одновременно."""
    board = Board(
        title="Original Title",
        description="Original Description",
        is_public=False,
        owner_id=default_auth_user.id,
    )
    db_session.add(board)
    await db_session.commit()
    await db_session.refresh(board)

    original_created_at = board.created_at

    response = await default_auth_client.patch(
        f"/api/v1/boards/{board.id}",
        json={
            "title": "Updated Title",
            "description": "Updated Description",
            "is_public": True,
        },
    )
    assert response.status_code == 200
    data = response.json()

    await db_session.refresh(board)

    expected_response = {
        "id": str(board.id),
        "title": board.title,
        "description": board.description,
        "is_public": board.is_public,
        "owner_id": str(board.owner_id),
        "team_id": str(board.team_id) if board.team_id else None,
        "created_at": board.created_at.isoformat(),
        "updated_at": board.updated_at.isoformat(),
    }
    assert data == expected_response

    expected_db_board = {
        "id": board.id,
        "title": "Updated Title",
        "description": "Updated Description",
        "is_public": True,
        "created_at": original_created_at,
        "updated_at": board.updated_at,
    }
    assert {
        "id": board.id,
        "title": board.title,
        "description": board.description,
        "is_public": board.is_public,
        "created_at": board.created_at,
        "updated_at": board.updated_at,
    } == expected_db_board
