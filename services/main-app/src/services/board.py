from uuid import UUID

from fastapi import Depends

from models import Board
from repositories.board import BoardRepository, get_board_repository
from schemas.board import CreateBoardRequest, UpdateBoardRequest


class BoardService:
    def __init__(self, repository: BoardRepository):
        self.repository = repository

    async def get(self, board_id: UUID) -> Board | None:
        return await self.repository.get_by_id(board_id)

    async def get_many(self, skip: int = 0, limit: int = 100) -> list[Board]:
        return await self.repository.get_all(skip=skip, limit=limit)

    async def create(self, board_data: CreateBoardRequest) -> Board:
        data = {
            "title": board_data.title,
            "description": board_data.description,
            "is_public": board_data.is_public,
            "owner_id": board_data.owner_id,
            "team_id": board_data.team_id,
        }
        return await self.repository.create(data)

    async def update(self, board_id: UUID, board_data: UpdateBoardRequest) -> Board:
        data = {}
        if board_data.title is not None:
            data["title"] = board_data.title
        if board_data.description is not None:
            data["description"] = board_data.description
        if board_data.is_public is not None:
            data["is_public"] = board_data.is_public
        if board_data.team_id is not None:
            data["team_id"] = board_data.team_id

        return await self.repository.update(board_id, data)

    async def delete(self, board_id: UUID) -> bool:
        return await self.repository.delete(board_id)


async def get_board_service(
    repository: BoardRepository = Depends(get_board_repository),
) -> BoardService:
    return BoardService(repository)
