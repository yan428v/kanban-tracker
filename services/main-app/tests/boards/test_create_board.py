import uuid

import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models import Board, User


@pytest.mark.asyncio(loop_scope="session")
async def test_create_board_title_only(
    default_auth_client: AsyncClient,
    default_auth_user: User,
    db_session: AsyncSession,
):
    """Создание доски только с обязательными полями."""
    response = await default_auth_client.post(
        "/api/v1/boards",
        json={"title": "Test Board", "owner_id": str(default_auth_user.id)},
    )
    assert response.status_code == 201
    data = response.json()

    board_id = uuid.UUID(data["id"])
    result = await db_session.execute(select(Board).where(Board.id == board_id))
    board_in_db = result.scalar_one()

    expected_response = {
        "id": str(board_in_db.id),
        "title": board_in_db.title,
        "description": board_in_db.description,
        "is_public": board_in_db.is_public,
        "owner_id": str(board_in_db.owner_id),
        "team_id": str(board_in_db.team_id) if board_in_db.team_id else None,
        "created_at": board_in_db.created_at.isoformat(),
        "updated_at": board_in_db.updated_at.isoformat(),
    }
    assert data == expected_response

    assert board_in_db.title == "Test Board"
    assert board_in_db.description is None
    assert board_in_db.is_public is False
    assert board_in_db.team_id is None


@pytest.mark.asyncio(loop_scope="session")
async def test_create_board_with_all_fields(
    default_auth_client: AsyncClient,
    default_auth_user: User,
    db_session: AsyncSession,
):
    """Создание доски со всеми полями."""
    response = await default_auth_client.post(
        "/api/v1/boards",
        json={
            "title": "Full Board",
            "description": "Board Description",
            "is_public": True,
            "owner_id": str(default_auth_user.id),
        },
    )
    assert response.status_code == 201
    data = response.json()

    board_id = uuid.UUID(data["id"])
    result = await db_session.execute(select(Board).where(Board.id == board_id))
    board_in_db = result.scalar_one()

    assert board_in_db.title == "Full Board"
    assert board_in_db.description == "Board Description"
    assert board_in_db.is_public is True


@pytest.mark.asyncio(loop_scope="session")
async def test_create_board_no_title(
    default_auth_client: AsyncClient, default_auth_user: User
):
    """Создание доски без title должно вернуть 422."""
    response = await default_auth_client.post(
        "/api/v1/boards", json={"owner_id": str(default_auth_user.id)}
    )
    assert response.status_code == 422
    data = response.json()
    assert any(error["loc"] == ["body", "title"] for error in data["detail"])


@pytest.mark.asyncio(loop_scope="session")
async def test_create_board_no_owner_id(default_auth_client: AsyncClient):
    """Создание доски без owner_id должно вернуть 422."""
    response = await default_auth_client.post(
        "/api/v1/boards", json={"title": "Test Board"}
    )
    assert response.status_code == 422
    data = response.json()
    assert any(error["loc"] == ["body", "owner_id"] for error in data["detail"])


@pytest.mark.asyncio(loop_scope="session")
async def test_create_board_empty_body(default_auth_client: AsyncClient):
    """Создание доски с пустым телом должно вернуть 422."""
    response = await default_auth_client.post("/api/v1/boards", json={})
    assert response.status_code == 422
