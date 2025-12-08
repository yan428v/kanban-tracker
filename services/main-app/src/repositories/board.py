from typing import Optional
from uuid import UUID

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models import Board
from core.database import get_session


class BoardRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, board_id: UUID) -> Optional[Board]:
        result = await self.db.execute(
            select(Board)
            .where(Board.id == board_id)
        )

        return result.scalar_one_or_none()

    async def get_all(self, skip: int = 0, limit: int = 100) -> list[Board]:
        result = await self.db.execute(
            select(Board)
            .offset(skip)
            .limit(limit))

        return result.scalars().all()

    async def get_by_owner_id(self, owner_id: UUID, skip: int = 0, limit: int = 100) -> list[Board]:
        result = await self.db.execute(
            select(Board)
            .where(Board.owner_id == owner_id)
            .offset(skip)
            .limit(limit)
        )

        return result.scalars().all()

    async def get_by_team_id(self, team_id: UUID, skip: int = 0, limit: int = 100) -> list[Board]:
        result = await self.db.execute(
            select(Board)
            .where(Board.team_id == team_id)
            .offset(skip)
            .limit(limit)
        )

        return result.scalars().all()

    async def create(self, board_data: dict) -> Board:
        board = Board(**board_data)
        self.db.add(board)
        await self.db.commit()
        await self.db.refresh(board)
        return board

    async def update(self, board_id: UUID, board_data: dict) -> Board:
        board = await self.get_by_id(board_id)

        if board:
            for key, value in board_data.items():
                setattr(board, key, value)

            await self.db.commit()
            await self.db.refresh(board)

        return board

    async def delete(self, board_id: UUID) -> bool:
        board = await self.get_by_id(board_id)

        if board:
            await self.db.delete(board)
            await self.db.commit()

            return True

        return False

    async def search_by_title(
        self, title_pattern: str, skip: int = 0, limit: int = 100
    ) -> list[Board]:
        result = await self.db.execute(
            select(Board)
            .where(Board.title.ilike(f"%{title_pattern}%"))
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()


async def get_board_repository(
    db: AsyncSession = Depends(get_session),
) -> BoardRepository:
    return BoardRepository(db)
