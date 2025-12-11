from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from models import Board
from schemas.board import BoardResponse, CreateBoardRequest, UpdateBoardRequest
from services.board import BoardService, get_board_service

router = APIRouter()

BOARD_NOT_FOUND_MESSAGE = "Board not found"


@router.get("/boards", response_model=list[BoardResponse])
async def list_boards(
    skip: int = 0,
    limit: int = 100,
    service: BoardService = Depends(get_board_service),
):
    boards = await service.get_many(skip=skip, limit=limit)
    return [board_to_response(board) for board in boards]


@router.get("/boards/{board_id}", response_model=BoardResponse)
async def get_board(
    board_id: UUID,
    service: BoardService = Depends(get_board_service),
):
    board = await service.get(board_id)
    if not board:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=BOARD_NOT_FOUND_MESSAGE
        )
    return board_to_response(board)


@router.post("/boards", response_model=BoardResponse, status_code=status.HTTP_201_CREATED)
async def create_board(
    board_data: CreateBoardRequest,
    service: BoardService = Depends(get_board_service),
):
    board = await service.create(board_data)
    return board_to_response(board)


@router.patch("/boards/{board_id}", response_model=BoardResponse)
async def update_board(
    board_id: UUID,
    board_data: UpdateBoardRequest,
    service: BoardService = Depends(get_board_service),
):
    board = await service.update(board_id, board_data)
    if not board:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=BOARD_NOT_FOUND_MESSAGE
        )
    return board_to_response(board)


@router.delete("/boards/{board_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_board(
    board_id: UUID,
    service: BoardService = Depends(get_board_service),
):
    result = await service.delete(board_id)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=BOARD_NOT_FOUND_MESSAGE
        )


def board_to_response(board: Board) -> BoardResponse:
    return BoardResponse(
        id=board.id,
        title=board.title,
        description=board.description,
        is_public=board.is_public,
        owner_id=board.owner_id,
        team_id=board.team_id,
        created_at=board.created_at,
        updated_at=board.updated_at,
    )
