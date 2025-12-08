from typing import Optional
from uuid import UUID

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models import BoardColumn
from core.database import get_session


class ColumnRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, column_id: UUID) -> Optional[BoardColumn]:
        result = await self.db.execute(
            select(BoardColumn)
            .where(BoardColumn.id == column_id)
        )

        return result.scalar_one_or_none()

    async def get_all(self, skip: int = 0, limit: int = 100) -> list[BoardColumn]:
        result = await self.db.execute(
            select(BoardColumn)
            .offset(skip)
            .limit(limit))

        return result.scalars().all()

    async def get_by_board_id(self, board_id: UUID, skip: int = 0, limit: int = 100) -> list[BoardColumn]:
        result = await self.db.execute(
            select(BoardColumn)
            .where(BoardColumn.board_id == board_id)
            .offset(skip)
            .limit(limit)
        )

        return result.scalars().all()

    async def create(self, column_data: dict) -> BoardColumn:
        column = BoardColumn(**column_data)
        self.db.add(column)
        await self.db.commit()
        await self.db.refresh(column)
        return column

    async def update(self, column_id: UUID, column_data: dict) -> BoardColumn:
        column = await self.get_by_id(column_id)

        if column:
            for key, value in column_data.items():
                setattr(column, key, value)

            await self.db.commit()
            await self.db.refresh(column)

        return column

    async def delete(self, column_id: UUID) -> bool:
        column = await self.get_by_id(column_id)

        if column:
            await self.db.delete(column)
            await self.db.commit()

            return True

        return False

    async def search_by_title(
        self, title_pattern: str, skip: int = 0, limit: int = 100
    ) -> list[BoardColumn]:
        result = await self.db.execute(
            select(BoardColumn)
            .where(BoardColumn.title.ilike(f"%{title_pattern}%"))
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()


async def get_column_repository(
    db: AsyncSession = Depends(get_session),
) -> ColumnRepository:
    return ColumnRepository(db)
