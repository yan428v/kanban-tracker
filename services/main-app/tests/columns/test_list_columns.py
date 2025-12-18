import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from models import Board, BoardColumn, User


@pytest.mark.asyncio(loop_scope="session")
async def test_no_columns(default_auth_client: AsyncClient):
    """Получение пустого списка колонок."""
    response = await default_auth_client.get("/api/v1/columns")
    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.asyncio(loop_scope="session")
async def test_two_columns_no_params(
    default_auth_client: AsyncClient,
    default_auth_user: User,
    db_session: AsyncSession,
):
    """Получение списка из двух колонок."""
    board = Board(title="Test Board", owner_id=default_auth_user.id)
    db_session.add(board)
    await db_session.commit()
    await db_session.refresh(board)

    column1 = BoardColumn(title="Column 1", board_id=board.id)
    column2 = BoardColumn(title="Column 2", board_id=board.id)
    db_session.add(column1)
    db_session.add(column2)
    await db_session.commit()
    await db_session.refresh(column1)
    await db_session.refresh(column2)

    response = await default_auth_client.get("/api/v1/columns")
    assert response.status_code == 200
    data = response.json()

    expected = [
        {
            "id": str(column1.id),
            "title": column1.title,
            "position": column1.position,
            "limit": column1.limit,
            "board_id": str(column1.board_id),
            "created_at": column1.created_at.isoformat(),
            "updated_at": column1.updated_at.isoformat(),
        },
        {
            "id": str(column2.id),
            "title": column2.title,
            "position": column2.position,
            "limit": column2.limit,
            "board_id": str(column2.board_id),
            "created_at": column2.created_at.isoformat(),
            "updated_at": column2.updated_at.isoformat(),
        },
    ]
    assert data == expected


@pytest.mark.asyncio(loop_scope="session")
async def test_skip_10(
    default_auth_client: AsyncClient,
    default_auth_user: User,
    db_session: AsyncSession,
):
    """Пропуск 10 колонок должен вернуть пустой список."""
    board = Board(title="Test Board", owner_id=default_auth_user.id)
    db_session.add(board)
    await db_session.commit()
    await db_session.refresh(board)

    column1 = BoardColumn(title="Column 1", board_id=board.id)
    column2 = BoardColumn(title="Column 2", board_id=board.id)
    db_session.add(column1)
    db_session.add(column2)
    await db_session.commit()

    response = await default_auth_client.get("/api/v1/columns?skip=10")
    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.asyncio(loop_scope="session")
async def test_limit_1(
    default_auth_client: AsyncClient,
    default_auth_user: User,
    db_session: AsyncSession,
):
    """Лимит 1 должен вернуть только первую колонку."""
    board = Board(title="Test Board", owner_id=default_auth_user.id)
    db_session.add(board)
    await db_session.commit()
    await db_session.refresh(board)

    column1 = BoardColumn(title="Column 1", board_id=board.id)
    column2 = BoardColumn(title="Column 2", board_id=board.id)
    db_session.add(column1)
    db_session.add(column2)
    await db_session.commit()
    await db_session.refresh(column1)

    response = await default_auth_client.get("/api/v1/columns?limit=1")
    assert response.status_code == 200
    data = response.json()

    expected = [
        {
            "id": str(column1.id),
            "title": column1.title,
            "position": column1.position,
            "limit": column1.limit,
            "board_id": str(column1.board_id),
            "created_at": column1.created_at.isoformat(),
            "updated_at": column1.updated_at.isoformat(),
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

    column1 = BoardColumn(title="Column 1", board_id=board.id)
    db_session.add(column1)
    await db_session.commit()
    await db_session.refresh(column1)

    response = await default_auth_client.get("/api/v1/columns?skip=-1")
    assert response.status_code == 200
    data = response.json()

    expected = [
        {
            "id": str(column1.id),
            "title": column1.title,
            "position": column1.position,
            "limit": column1.limit,
            "board_id": str(column1.board_id),
            "created_at": column1.created_at.isoformat(),
            "updated_at": column1.updated_at.isoformat(),
        }
    ]
    assert data == expected
