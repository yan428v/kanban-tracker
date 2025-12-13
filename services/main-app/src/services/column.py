from uuid import UUID

from fastapi import Depends

from models import BoardColumn
from repositories.column import ColumnRepository, get_column_repository
from schemas.column import CreateColumnRequest, UpdateColumnRequest


class ColumnService:
    def __init__(self, repository: ColumnRepository):
        self.repository = repository

    async def get(self, column_id: UUID) -> BoardColumn | None:
        return await self.repository.get_by_id(column_id)

    async def get_many(self, skip: int = 0, limit: int = 100) -> list[BoardColumn]:
        return await self.repository.get_all(skip=skip, limit=limit)

    async def create(self, column_data: CreateColumnRequest) -> BoardColumn:
        data = {
            "title": column_data.title,
            "position": column_data.position,
            "limit": column_data.limit,
            "board_id": column_data.board_id,
        }
        return await self.repository.create(data)

    async def update(
        self, column_id: UUID, column_data: UpdateColumnRequest
    ) -> BoardColumn:
        data = {}
        if column_data.title is not None:
            data["title"] = column_data.title
        if column_data.position is not None:
            data["position"] = column_data.position
        if column_data.limit is not None:
            data["limit"] = column_data.limit

        return await self.repository.update(column_id, data)

    async def delete(self, column_id: UUID) -> bool:
        return await self.repository.delete(column_id)


async def get_column_service(
    repository: ColumnRepository = Depends(get_column_repository),
) -> ColumnService:
    return ColumnService(repository)
