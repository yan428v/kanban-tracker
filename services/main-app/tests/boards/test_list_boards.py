import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from models import Board, User


@pytest.mark.asyncio(loop_scope="session")
async def test_no_boards(default_auth_client: AsyncClient):
    """Получение пустого списка досок."""
    response = await default_auth_client.get("/api/v1/boards")
    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.asyncio(loop_scope="session")
async def test_two_boards_no_params(
    default_auth_client: AsyncClient,
    default_auth_user: User,
    db_session: AsyncSession,
):
    """Получение списка из двух досок."""
    board1 = Board(title="Board 1", owner_id=default_auth_user.id)
    board2 = Board(title="Board 2", owner_id=default_auth_user.id)
    db_session.add(board1)
    db_session.add(board2)
    await db_session.commit()
    await db_session.refresh(board1)
    await db_session.refresh(board2)

    response = await default_auth_client.get("/api/v1/boards")
    assert response.status_code == 200
    data = response.json()

    expected = [
        {
            "id": str(board1.id),
            "title": board1.title,
            "description": board1.description,
            "is_public": board1.is_public,
            "owner_id": str(board1.owner_id),
            "team_id": str(board1.team_id) if board1.team_id else None,
            "created_at": board1.created_at.isoformat(),
            "updated_at": board1.updated_at.isoformat(),
        },
        {
            "id": str(board2.id),
            "title": board2.title,
            "description": board2.description,
            "is_public": board2.is_public,
            "owner_id": str(board2.owner_id),
            "team_id": str(board2.team_id) if board2.team_id else None,
            "created_at": board2.created_at.isoformat(),
            "updated_at": board2.updated_at.isoformat(),
        },
    ]
    assert data == expected


@pytest.mark.asyncio(loop_scope="session")
async def test_skip_10(
    default_auth_client: AsyncClient,
    default_auth_user: User,
    db_session: AsyncSession,
):
    """Пропуск 10 досок должен вернуть пустой список."""
    board1 = Board(title="Board 1", owner_id=default_auth_user.id)
    board2 = Board(title="Board 2", owner_id=default_auth_user.id)
    db_session.add(board1)
    db_session.add(board2)
    await db_session.commit()

    response = await default_auth_client.get("/api/v1/boards?skip=10")
    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.asyncio(loop_scope="session")
async def test_limit_1(
    default_auth_client: AsyncClient,
    default_auth_user: User,
    db_session: AsyncSession,
):
    """Лимит 1 должен вернуть только первую доску."""
    board1 = Board(title="Board 1", owner_id=default_auth_user.id)
    board2 = Board(title="Board 2", owner_id=default_auth_user.id)
    db_session.add(board1)
    db_session.add(board2)
    await db_session.commit()
    await db_session.refresh(board1)

    response = await default_auth_client.get("/api/v1/boards?limit=1")
    assert response.status_code == 200
    data = response.json()

    expected = [
        {
            "id": str(board1.id),
            "title": board1.title,
            "description": board1.description,
            "is_public": board1.is_public,
            "owner_id": str(board1.owner_id),
            "team_id": str(board1.team_id) if board1.team_id else None,
            "created_at": board1.created_at.isoformat(),
            "updated_at": board1.updated_at.isoformat(),
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
    board1 = Board(title="Board 1", owner_id=default_auth_user.id)
    db_session.add(board1)
    await db_session.commit()
    await db_session.refresh(board1)

    response = await default_auth_client.get("/api/v1/boards?skip=-1")
    assert response.status_code == 200
    data = response.json()

    expected = [
        {
            "id": str(board1.id),
            "title": board1.title,
            "description": board1.description,
            "is_public": board1.is_public,
            "owner_id": str(board1.owner_id),
            "team_id": str(board1.team_id) if board1.team_id else None,
            "created_at": board1.created_at.isoformat(),
            "updated_at": board1.updated_at.isoformat(),
        }
    ]
    assert data == expected
